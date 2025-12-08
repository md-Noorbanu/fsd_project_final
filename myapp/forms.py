from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        # exclude user field, we will assign it from request.user in the view
        exclude = ['user']