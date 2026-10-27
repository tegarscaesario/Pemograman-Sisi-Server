# Simple LMS: Pemrograman Sisi Server

Project latihan **Simple LMS** untuk mata kuliah Pemrograman Sisi Server.
Dibangun dengan Django 5.2 dan PostgreSQL 17. Seluruh runtime dijalankan di Docker Compose, jadi Django dan PostgreSQL **tidak perlu di-install di komputer host**.

- **Minggu 4**: Django, ORM, Custom User, dan model inti LMS (Course, Lesson, Enrollment, Assignment, Submission).
- **Minggu 5**: optimasi database (N+1 query, `select_related`, `prefetch_related`, `EXPLAIN`, dan index).

## Struktur Project

```
.
├── manage.py
├── config/                      # pengaturan project Django
├── users/                       # Custom User (role: ADMIN, LECTURER, STUDENT)
├── catalog/                     # model LMS, admin, test, dan management command
│   ├── models.py
│   ├── tests.py
│   ├── migrations/
│   └── management/commands/
│       ├── seed_demo.py                   # sample data Minggu 4
│       ├── generate_performance_data.py   # 10.000 Course (Minggu 5)
│       └── generate_relationship_data.py  # data relasi LMS (Minggu 5)
├── bench_before.py              # Course + Lecturer, tanpa optimasi
├── bench_after.py               # Course + Lecturer, select_related
├── bench_lesson_before.py       # Course + Lesson, tanpa optimasi
├── bench_lesson_after.py        # Course + Lesson, prefetch_related
├── bench_index.py               # EXPLAIN ANALYZE untuk pengujian index
├── bench_lab_d.py               # exists, count, values, annotate
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── .env                         # tidak di-commit
```

## Menjalankan Project

### 1. Buat file `.env`

File `.env` tidak ikut repository. Buat sendiri di root project:

```
DB_NAME= #sample lms_db
DB_USER= #sample lms_user
DB_PASSWORD= #sample lms_password
```


### 2. Build dan jalankan container

```
docker compose build
docker compose up -d
docker compose ps
```

Service `app` dan `db` harus berstatus **Up**. Aplikasi berjalan di http://localhost:8000.

### 3. Migrasi database

```
docker compose exec app python manage.py migrate
docker compose exec app python manage.py check
```

### 4. Buat superuser (opsional, untuk Django Admin)

```
docker compose exec app python manage.py createsuperuser
```

Login di http://localhost:8000/admin/. Role superuser dapat diubah menjadi `ADMIN` lewat Django Shell.

## Membuat Dataset Pengujian (Minggu 5)

Perintah di bawah aman dijalankan berulang (repeatable): data yang sudah ada tidak dibuat ulang. **Urutannya harus seperti ini.**

**1. Buat 10.000 Course (kode `PERF00000` sampai `PERF09999`)**

Perintah ini membutuhkan minimal satu User dengan role `LECTURER`.

```
docker compose exec app python manage.py generate_performance_data
```

**2. Buat data relasi untuk 100 Course PERF pertama**

```
docker compose exec app python manage.py generate_relationship_data
```

Data yang dibuat: 5 dosen simulasi, 50 mahasiswa simulasi, 1.000 Enrollment, 500 Lesson, 200 Assignment, dan 1.000 Submission.

**3. Cek jumlah data**

```
docker compose exec app python manage.py shell -c "from catalog.models import Course; print(Course.objects.count())"
```

## Mengulang Benchmark

Jalankan dari root project. Gunakan data dan kondisi yang sama saat membandingkan BEFORE dan AFTER. Waktu eksekusi bisa sedikit berbeda di tiap komputer, jadi sebaiknya jalankan beberapa kali dan catat rata-ratanya.

### Course + Lecturer (`select_related`)

```
docker compose exec -T app python manage.py shell < bench_before.py
docker compose exec -T app python manage.py shell < bench_after.py
```

### Course + Lesson (`prefetch_related`)

```
docker compose exec -T app python manage.py shell < bench_lesson_before.py
docker compose exec -T app python manage.py shell < bench_lesson_after.py
```

### Teknik lain: `exists`, `count`, `values`, `annotate`

```
docker compose exec -T app python manage.py shell < bench_lab_d.py
```

### Database Index (`EXPLAIN`)

Index didefinisikan di `catalog/models.py` pada class `Meta` milik `Course`:

```python
indexes = [
    models.Index(fields=["is_active", "title"]),
]
```

Untuk membandingkan sebelum dan sesudah index, lepas migrasi index (migrasi `0005`), jalankan benchmark, pasang kembali, lalu jalankan benchmark lagi:

```
# BEFORE: lepas index
docker compose exec app python manage.py migrate catalog 0004
docker compose exec -T app python manage.py shell < bench_index.py

# AFTER: pasang index
docker compose exec app python manage.py migrate
docker compose exec -T app python manage.py shell < bench_index.py
```

## Hasil Benchmark

Hasil dari satu kali percobaan pada dataset 10.005 Course. Angka waktu dapat berbeda pada komputer lain.

| Percobaan | BEFORE | AFTER |
|---|---|---|
| Course + Lecturer (100 Course) | 101 query, 0,0532 detik | 1 query, 0,0186 detik |
| Course + Lesson (50 Course) | 51 query, 0,0425 detik | 2 query, 0,0206 detik |
| Index (`is_active`, `title`) | Seq Scan, cost 239.07, 0,696 ms | Index Scan, cost 8.31, 0,031 ms |

Kesimpulan singkat:

- `select_related()` memakai SQL JOIN, cocok untuk relasi ForeignKey (Course ke Lecturer).
- `prefetch_related()` mengambil relasi satu-ke-banyak dengan satu query tambahan (Course ke Lesson).
- Index mengubah rencana query dari Seq Scan menjadi Index Scan. Trade-off: ruang penyimpanan tambahan dan biaya INSERT, UPDATE, dan DELETE yang lebih besar.

## Menjalankan Test

```
docker compose exec app python manage.py test catalog
```

Hasil yang diharapkan: `Ran 3 tests ... OK`.

## Catatan

- File `.env` tidak boleh di-commit.
- File migrasi di `users/migrations/` dan `catalog/migrations/` ikut di-commit agar project dapat direproduksi.
- Untuk menghentikan container: `docker compose down`. Tambahkan `-v` hanya jika ingin menghapus seluruh data database.
