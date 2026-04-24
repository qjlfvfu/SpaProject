import requests
from django.conf import settings
from celery import shared_task

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


def send_telegram_message(chat_id, text):
    """Отправка сообщения"""
    url = f"{TELEGRAM_API}/sendMessage"
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    return requests.post(url, data=data).json()


@shared_task
def send_habit_reminder(chat_id, habit_name, action, time):
    """Отправка напоминания о привычке"""
    message = f"""
🔔 <b>Напоминание о привычке!</b>

<b>Действие:</b> {action}
<b>Время:</b> {time}
<b>Привычка:</b> {habit_name}
    """
    send_telegram_message(chat_id, message)