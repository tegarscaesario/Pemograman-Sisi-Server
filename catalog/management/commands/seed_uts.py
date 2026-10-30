from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from catalog.models import Assignment, Course, Enrollment, Lesson, Submission
from users.models import User


class Command(BaseCommand):
    help = "Data minimal UTS Soal 4a (idempotent: aman dijalankan berulang)"

    @transaction.atomic
    def handle(self, *args, **options):
        # 1 dosen + 2 mahasiswa
        dosen, _ = User.objects.get_or_create(
            username="dosen_uts",
            defaults={"email": "dosen_uts@example.com", "role": User.Role.LECTURER},
        )
        mhs1, _ = User.objects.get_or_create(
            username="mahasiswa_uts1",
            defaults={"email": "mhs1@example.com", "role": User.Role.STUDENT},
        )
        mhs2, _ = User.objects.get_or_create(
            username="mahasiswa_uts2",
            defaults={"email": "mhs2@example.com", "role": User.Role.STUDENT},
        )
        for u in (dosen, mhs1, mhs2):
            if not u.has_usable_password():
                u.set_password("uts12345")
                u.save(update_fields=["password"])

        # 2 Course
        uts1, _ = Course.objects.get_or_create(
            code="UTS01",
            defaults={
                "title": "Pemrograman Sisi Server",
                "description": "Backend dengan Django dan PostgreSQL",
                "lecturer": dosen,
            },
        )
        uts2, _ = Course.objects.get_or_create(
            code="UTS02",
            defaults={
                "title": "Basis Data Lanjut",
                "description": "Optimasi query dan indexing",
                "lecturer": dosen,
            },
        )

        # 3 Lesson pada UTS01
        for order, title in enumerate(
            ["Backend Fundamentals", "Architectural Patterns", "Docker"], start=1
        ):
            Lesson.objects.get_or_create(
                course=uts1,
                order=order,
                defaults={"title": title, "content": f"Materi {title}"},
            )

        # 2 Enrollment
        Enrollment.objects.get_or_create(student=mhs1, course=uts1)
        Enrollment.objects.get_or_create(student=mhs2, course=uts1)

        # 1 Assignment + 1 Submission
        tugas, _ = Assignment.objects.get_or_create(
            course=uts1,
            title="Tugas Django ORM",
            defaults={
                "description": "Implementasi model dan relasi.",
                "deadline": timezone.now() + timedelta(days=7),
            },
        )
        Submission.objects.get_or_create(
            assignment=tugas,
            student=mhs1,
            defaults={"content": "Jawaban tugas Django ORM.", "grade": 85},
        )

        self.stdout.write(self.style.SUCCESS("Data UTS Soal 4a siap."))
        for label, qs in [
            ("Dosen", User.objects.filter(username="dosen_uts")),
            ("Mahasiswa", User.objects.filter(username__startswith="mahasiswa_uts")),
            ("Course UTS", Course.objects.filter(code__startswith="UTS")),
            ("Lesson UTS01", Lesson.objects.filter(course=uts1)),
            ("Enrollment UTS01", Enrollment.objects.filter(course=uts1)),
            ("Assignment UTS01", Assignment.objects.filter(course=uts1)),
            ("Submission UTS01", Submission.objects.filter(assignment__course=uts1)),
        ]:
            self.stdout.write(f"{label}: {qs.count()}")
