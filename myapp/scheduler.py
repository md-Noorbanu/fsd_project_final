from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Reminder
from .utils import send_notification

scheduler = BackgroundScheduler()

def check_reminders():
    now = timezone.now()
    reminders = Reminder.objects.filter(
        reminder_time__lte=now,
        notified=False
    )

    for reminder in reminders:
        send_notification(reminder.title, reminder.message)
        reminder.notified = True
        reminder.save()

def start():
    if not scheduler.running:
        scheduler.add_job(check_reminders, 'interval', seconds=30)
        scheduler.start()