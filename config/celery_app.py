import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# -------------------------------
# Celery Beat schedule file
# -------------------------------
app.conf.beat_schedule_filename = os.getenv(
    "CELERY_BEAT_SCHEDULE_FILE",
    "var/celery/celerybeat-schedule",
)