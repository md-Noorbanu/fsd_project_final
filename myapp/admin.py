
# Register your models here.
from django.contrib import admin
from .models import Member, Reminder

admin.site.register(Member)
admin.site.register(Reminder)