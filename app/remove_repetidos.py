from app.models import *

es = User.objects.values_list('email', flat=True).distinct()

for e in es:
    if len(User.objects.filter(email=e))>1:
       print(e, User.objects.filter(email=e))