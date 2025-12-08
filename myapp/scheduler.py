from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Reminder
from .utils import send_notification

scheduler = BackgroundScheduler()

def check_reminders():
    """Check DB for reminders whose combined date+time is <= now and not yet notified.

    This uses the current Reminder model which stores `date` and `time` separately.
    When a match is found we call `send_notification` (server log) and mark as notified.
    """
    now = timezone.localtime()
    # fetch candidates that are not yet notified
    candidates = Reminder.objects.filter(notified=False)
    for r in candidates:
        try:
            dt = timezone.make_aware(__import__('datetime').datetime.combine(r.date, r.time), timezone.get_default_timezone())
        except Exception:
            # fallback: skip invalid entries
            continue
        try:
            dt_local = timezone.localtime(dt)
        except Exception:
            dt_local = dt
        if dt_local <= now:
            # server-side notification (console/log) — real browser notifications require the client
            send_notification(r.medicine_name, r.dosage or '')
            r.notified = True
            r.save()

def start():
    if not scheduler.running:
        scheduler.add_job(check_reminders, 'interval', seconds=30)
        scheduler.start()