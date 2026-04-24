from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminder(chat_id, habit_name, action, time_str):
    """Отправка напоминания о привычке"""
    message = f"""
🔔 <b>НАПОМИНАНИЕ О ПРИВЫЧКЕ!</b>

<b>Привычка:</b> {habit_name}
<b>Действие:</b> {action}
<b>Время:</b> {time_str}

Не забывайте выполнить! У вас есть 2 минуты ⏱️
    """
    send_telegram_message(chat_id, message)


@shared_task
def check_and_send_reminders():
    """Проверка и отправка напоминаний (запускается каждую минуту)"""
    now = timezone.now()
    current_time = now.time()

    # Приводим к минутам без секунд (для точного совпадения)
    current_time = current_time.replace(second=0, microsecond=0)

    # Ищем привычки, у которых время наступило или прошло (с запасом 1 минута)
    time_threshold = (
        (now - timedelta(minutes=1)).time().replace(second=0, microsecond=0)
    )

    habits = Habit.objects.filter(
        time__lte=current_time,  # время наступило или прошло
        time__gte=time_threshold,  # не старше 1 минуты (не спамим старыми)
        period__gte=1,
        period__lte=7,
        is_pleasant=False,
        is_active=True,  # если есть такое поле
    )

    sent_count = 0
    for habit in habits:
        # Проверяем, нужно ли напоминать
        if habit.needs_reminder() and habit.customer.telegram_chat_id:
            send_habit_reminder.delay(
                habit.customer.telegram_chat_id,
                habit.name,
                habit.action,
                habit.time.strftime("%H:%M"),
            )
            habit.last_sent = now
            habit.save(update_fields=["last_sent"])
            sent_count += 1

    if sent_count:
        print(f"Отправлено {sent_count} напоминаний")

    return f"Отправлено {sent_count} напоминаний"


@shared_task
def send_telegram_message_task(chat_id, message):
    """Обёртка для отправки сообщения через Celery"""
    send_telegram_message(chat_id, message)
