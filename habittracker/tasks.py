from celery import shared_task
from django.utils import timezone
from .models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminder(chat_id, habit_name, action, time_str):
    """Отправка напоминания о привычке"""
    message = f"""
🔔 <b>Напоминание о привычке!</b>

<b>Привычка:</b> {habit_name}
<b>Действие:</b> {action}
<b>Время:</b> {time_str}
    """
    send_telegram_message(chat_id, message)


@shared_task
def check_and_send_reminders():
    """Проверка и отправка напоминаний"""
    now = timezone.now()
    current_time = now.time()

    # Округляем минуты до ближайших 5 (чтобы не спамить)
    # current_time = current_time.replace(minute=current_time.minute - current_time.minute % 5, second=0, microsecond=0)

    habits = Habit.objects.filter(
        time__lte=current_time,  # 'time__lte' — время прошло или наступило
        period__gte=1,
        period__lte=7,
        is_pleasant=False
    )

    for habit in habits:
        # Проверка для сегодняшнего дня
        if habit.needs_reminder() and habit.customer.telegram_chat_id:
            send_habit_reminder.delay(
                habit.customer.telegram_chat_id,
                habit.name,
                habit.action,
                habit.time.strftime('%H:%M')
            )
            habit.last_sent = now
            habit.save(update_fields=['last_sent'])