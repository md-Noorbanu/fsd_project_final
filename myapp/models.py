from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name


class Reminder(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    medicine_name = models.CharField(max_length=100)
    time = models.TimeField()
    date = models.DateField()
    dosage = models.CharField(max_length=50)
    notified = models.BooleanField(default=False)
    datetime = models.DateTimeField(help_text="Combined date and time for the reminder")
    is_notified = models.BooleanField(default=False, help_text="Whether notification has been sent")

    class Meta:
        pass

    def __str__(self):
        return f"{self.medicine_name} - {self.member.name}"


class ReminderHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reminder_title = models.CharField(max_length=200)
    action = models.CharField(max_length=20)
    old_data = models.TextField(blank=True)
    new_data = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.reminder_title} ({self.created_at})"