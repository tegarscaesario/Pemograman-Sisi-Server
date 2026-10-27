from catalog.models import Course, Enrollment
from django.db.models import Count

# A. exists()
course = Course.objects.get(code="PERF00001")
ada_mahasiswa = Enrollment.objects.filter(course=course).exists()
print("A. Ada mahasiswa terdaftar:", ada_mahasiswa)

# B. count()
jumlah_course = Course.objects.filter(code__startswith="PERF").count()
print("B. Jumlah Course simulasi:", jumlah_course)

# C. values()
print("C. values():")
for row in Course.objects.filter(code__startswith="PERF").values("code", "title")[:5]:
    print("  ", row)

# D. annotate()
print("D. annotate():")
courses = Course.objects.filter(code__startswith="PERF").annotate(jumlah_mahasiswa=Count("enrollments")).order_by("code")[:5]
for c in courses:
    print("  ", c.code, c.jumlah_mahasiswa)