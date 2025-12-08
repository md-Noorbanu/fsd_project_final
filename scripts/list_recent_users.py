import os
import sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE not in sys.path:
    sys.path.insert(0, BASE)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django
django.setup()
from django.contrib.auth.models import User

users = list(User.objects.all().order_by('-id').values('id','username','email','date_joined')[:10])
print('Last users:')
for u in users:
    print(u)
print('Total users:', User.objects.count())
