from django.apps import AppConfig
import os

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start
            start()