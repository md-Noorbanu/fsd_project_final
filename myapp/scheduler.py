from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import Reminder
from .utils import send_notification
from datetime import datetime as _dt

# make scheduler use Django's current timezone
scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())

def check_reminders():
    """Check DB for reminders whose combined date+time is <= now and not yet notified.

    This uses the current Reminder model which stores `date` and `time` separately.
    When a match is found we call `send_notification` (server log) and mark as notified.
    """
    now = timezone.localtime(timezone.now())
    # fetch candidates that are not yet notified
    candidates = Reminder.objects.filter(notified=False)
    for r in candidates:
        try:
            combined = _dt.combine(r.date, r.time)
        except Exception:
            # invalid date/time — skip
            continue
        # ensure timezone-aware using Django current timezone
        if timezone.is_naive(combined):
            combined = timezone.make_aware(combined, timezone.get_current_timezone())
        # convert to localtime for comparison
        try:
            combined_local = timezone.localtime(combined)
        except Exception:
            combined_local = combined
        if combined_local <= now:
            # server-side notification (console/log) — real browser notifications require the client
            send_notification(r.medicine_name, r.dosage or '')
            r.notified = True
            r.save()

def start():
    if not scheduler.running:
        # run immediately on start and then every 30s
        scheduler.add_job(check_reminders, 'interval', seconds=30, next_run_time=timezone.now())
        scheduler.start()