from django.apps import AppConfig
import os

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        # start the reminder scheduler when the app loads
        from . import scheduler
        scheduler.start()