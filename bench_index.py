from catalog.models import Course

qs = Course.objects.filter(is_active=True, title="Performance Course 5001")
print("Jumlah hasil:", qs.count())
print(qs.explain(analyze=True))
