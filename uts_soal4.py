# Jalankan: docker compose exec -T app python manage.py shell < uts_soal4.py
from catalog.models import Assignment, Course, Enrollment, Submission
from users.models import User

course = Course.objects.get(code="UTS01")
dosen = User.objects.get(username="dosen_uts")

print("=== 1. Semua Course beserta kode dan judulnya (10 pertama) ===")
print("Total Course:", Course.objects.count())
for c in Course.objects.all()[:10]:
    print(c.code, "-", c.title)

print("\n=== 2. Course yang diampu seorang dosen:", dosen.username, "===")
for c in Course.objects.filter(lecturer=dosen):
    print(c.code, "-", c.title)

print("\n=== 3. Semua Lesson milik Course", course.code, "===")
for lesson in course.lessons.all():
    print(lesson.order, "-", lesson.title)

print("\n=== 4. Jumlah mahasiswa terdaftar di", course.code, "===")
print(Enrollment.objects.filter(course=course).count())

print("\n=== 5. Semua Assignment milik", course.code, "===")
for a in Assignment.objects.filter(course=course):
    print(a.title, "| deadline:", a.deadline)

print("\n=== 6. Semua Submission milik Assignment pertama ===")
a = Assignment.objects.filter(course=course).first()
for s in Submission.objects.filter(assignment=a):
    print(s.student.username, "->", a.title, "| nilai:", s.grade)
