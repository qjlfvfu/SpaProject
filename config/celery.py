from celery import app
from celery.schedules import crontab

app.conf.beat_schedule = {
    "send-habit-reminders": {
        "task": "habittracker.tasks.check_and_send_reminders",
        "schedule": 60.0,  # каждую минуту
    },
    "check-missed-habits": {
        "task": "habittracker.tasks.check_missed_habits",
        "schedule": crontab(hour=22, minute=0),  # каждый день в 22:00
    },
}
