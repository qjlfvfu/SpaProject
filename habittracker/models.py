from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import CustomUser


# Create your models here.
class Habit(models.Model):
    name = models.CharField(
        max_length=30,
        help_text="Введите название привычки",
        null=False,
        verbose_name="Название привычки",
    )
    customer = models.ForeignKey(CustomUser, on_delete=CASCADE, related_name="habits")
    description = models.TextField(
        max_length=150,
        help_text="Введите описание привычки",
        null=True,
        verbose_name="Описание привычки",
    )
    place = models.CharField(
        max_length=40,
        help_text="Введите место выполнения",
        null=True,
        verbose_name="Место выполнения привычки",
    )
    action = models.CharField(
        max_length=200,
        verbose_name="Действие",
        help_text="Что именно нужно сделать (например, 'выходить на прогулку')",
    )
    is_pleasant = models.BooleanField(
        verbose_name="Приятная привычка?",
        choices=[(True, "Да"), (False, "Нет")],
        default=False,
    )
    planned_duration = models.DurationField(
        verbose_name="время на выполнения привычки",
        null=True,
        blank=True,
        default=None,
        help_text="сколько вы занимались привычкой?",
    )

    period = models.PositiveSmallIntegerField(
        verbose_name="Периодичность выполнения",
        default=1,
        help_text="Через сколько дней повторять привычку",
    )
    is_public = models.BooleanField(
        verbose_name="Публикация",
        default=False,
        choices=[(True, "Опубликовано"), (False, "Не опубликовано")],
    )
    reward = models.CharField(
        verbose_name="Награда за выполнение", default=None, blank=True, null=True
    )
    related_habit = models.ForeignKey(
        "self",
        verbose_name="Связанная привычка",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    time = models.TimeField(verbose_name="Время выполнения")
    last_sent = models.DateTimeField(
        verbose_name="Последнее напоминание",
        null=True,
        blank=True,
        help_text="Когда последний раз отправляли напоминание",
    )

    def needs_reminder(self):
        """Проверяет, пора ли отправить напоминание по этой привычке"""
        # 1. Проверяем, не отправляли ли уже сегодня
        if self.last_sent and self.last_sent.date() == timezone.now().date():
            return False

        # 2. Проверяем, была ли привычка выполнена сегодня
        today = timezone.now().date()
        has_completed = self.trackers.filter(
            completed_date=today,
            status=True,
            user=self.customer,  # важно: проверяем для конкретного пользователя
        ).exists()

        # 3. Если ещё не выполнена — напоминаем
        return not has_completed

    def get_next_reminder_time(self):
        """Возвращает следующее время для отправки напоминания"""
        return timezone.datetime.combine(timezone.now().date(), self.time)

    def __str__(self):
        return self.name

    def clean(self):
        """Все валидации должны быть здесь"""
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя заполнять одновременно награду и связанную привычку"
            )

        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError("Связанная привычка должна быть приятной")
        if self.planned_duration and self.planned_duration.total_seconds() > 120:
            raise ValidationError("Время выполнения не должно превышать 120 секунд")

        if self.period < 1 or self.period > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней")

        if self.is_pleasant and (self.reward or self.related_habit):
            raise ValidationError(
                "У приятной привычки не может быть награды или связанной привычки"
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # вызывает clean()
        super().save(*args, **kwargs)


class Tracker(models.Model):
    habit = models.ForeignKey(
        Habit,
        on_delete=CASCADE,
        help_text="привычка для отслеживания",
        related_name="trackers",
    )
    user = models.ForeignKey(CustomUser, on_delete=CASCADE, related_name="trackers")
    created_at = models.DateTimeField(
        verbose_name="Время создания трекера", auto_now_add=True
    )
    status = models.BooleanField(
        verbose_name="Статус выполнения",
        choices=[(True, "Выполнено"), (False, "Не выполнено")],
    )
    actual_duration = models.DurationField(
        verbose_name="Фактическое время выполнения", default=None, null=True
    )
    completed_date = models.DateField(
        verbose_name="Дата выполнения", auto_now_add=False
    )
    last_sent = models.DateTimeField(
        verbose_name="Последнее напоминание",
        null=True,
        blank=True,
        help_text="Когда последний раз отправляли напоминание",
    )

    def __str__(self):
        return f"{self.habit.name} - {self.completed_date} - {'Выполнено' if self.status else 'Не выполнено'}"

    def clean(self):
        if self.completed_date > timezone.now().date():
            raise ValidationError("Нельзя отметить выполнение в будущем")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ["habit", "user", "completed_date"]
        ordering = ["-completed_date"]
