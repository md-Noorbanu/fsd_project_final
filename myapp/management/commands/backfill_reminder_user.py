"""
Management command to backfill Reminder.user from Member.user for orphaned reminders.

Usage: python manage.py backfill_reminder_user
"""
from django.core.management.base import BaseCommand
from myapp.models import Reminder, Member


class Command(BaseCommand):
    help = 'Backfill Reminder.user from Member.user for reminders with null user'

    def handle(self, *args, **options):
        # Find all reminders with null user
        orphaned = Reminder.objects.filter(user__isnull=True)
        self.stdout.write(f"Found {orphaned.count()} reminders with null user")

        updated = 0
        skipped = 0
        for r in orphaned:
            if r.member and r.member.user:
                r.user = r.member.user
                r.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Updated reminder {r.id} ({r.medicine_name}) → user {r.user.username}'
                    )
                )
            else:
                skipped += 1
                self.stdout.write(
                    self.style.WARNING(f'  ⊗ Skipped reminder {r.id} (no member or member.user)')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nBackfill complete: {updated} updated, {skipped} skipped')
        )
