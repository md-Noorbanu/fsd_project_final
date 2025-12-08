from django.test import TestCase
from django.urls import reverse
from .models import Member, Reminder
from django.contrib.auth.models import User
from django.utils import timezone


class ReminderCrudTests(TestCase):
    def setUp(self):
        # create a user and member to attach reminders to
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.member = Member.objects.create(user=self.user, name='Test User', age=30, phone='1234567890')
        # log in the test client so protected views succeed
        self.client.login(username='testuser', password='pass')

    def test_add_reminder(self):
        url = reverse('reminder')
        data = {
            'member': self.member.id,
            'medicine_name': 'TestMed',
            'time': '09:00',
            'date': '2025-12-06',
            'dosage': '1 pill'
        }
        resp = self.client.post(url, data)
        # after successful create, view redirects to dashboard
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Reminder.objects.count(), 1)

    def test_edit_reminder(self):
        rem = Reminder.objects.create(member=self.member, user=self.user, medicine_name='OldMed', time='08:00', date='2025-12-06', dosage='1')
        url = reverse('editReminder', args=[rem.id])
        data = {
            'member': self.member.id,
            'medicine_name': 'NewMed',
            'time': '10:00',
            'date': '2025-12-07',
            'dosage': '2'
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 302)
        rem.refresh_from_db()
        self.assertEqual(rem.medicine_name, 'NewMed')

    def test_delete_reminder(self):
        rem = Reminder.objects.create(member=self.member, user=self.user, medicine_name='ToDelete', time='08:00', date='2025-12-06', dosage='1')
        url = reverse('deleteReminder', args=[rem.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Reminder.objects.filter(id=rem.id).count(), 0)

    def test_rempages_shows_reminders(self):
        Reminder.objects.create(member=self.member, user=self.user, medicine_name='ShowMed', time='08:00', date='2025-12-06', dosage='1')
        url = reverse('rempages')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'ShowMed')
from django.test import TestCase

# Create your tests here.
