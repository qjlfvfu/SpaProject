from datetime import timezone

from django import forms
from .models import Habit, Tracker


class HabitForm(forms.ModelForm):
    """Форма для создания и редактирования привычки"""

    class Meta:
        model = Habit
        fields = [
            "name",
            "action",
            "description",
            "place",
            "time",
            "planned_duration",
            "period",
            "is_pleasant",
            "is_public",
            "reward",
            "related_habit",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Утренняя зарядка",
                }
            ),
            "action": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: делать зарядку",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Подробное описание привычки",
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Дома, в спортзале",
                }
            ),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "planned_duration": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "HH:MM:SS (например, 00:02:00)",
                }
            ),
            "period": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 7}
            ),
            "is_pleasant": forms.Select(
                attrs={"class": "form-select"}, choices=[(True, "Да"), (False, "Нет")]
            ),
            "is_public": forms.Select(
                attrs={"class": "form-select"},
                choices=[(True, "Опубликовано"), (False, "Не опубликовано")],
            ),
            "reward": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Съесть шоколадку",
                }
            ),
            "related_habit": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "name": "Название привычки",
            "action": "Действие",
            "description": "Описание",
            "place": "Место выполнения",
            "time": "Время выполнения",
            "planned_duration": "Время на выполнение (сек)",
            "period": "Периодичность (дни)",
            "is_pleasant": "Приятная привычка?",
            "is_public": "Публичная?",
            "reward": "Награда",
            "related_habit": "Связанная привычка",
        }
        help_texts = {
            "period": "От 1 до 7 дней. Через сколько дней повторять привычку",
            "planned_duration": "Не должно превышать 120 секунд (2 минуты)",
            "reward": "Заполняется ТОЛЬКО для полезных привычек",
            "related_habit": "Заполняется ТОЛЬКО для полезных привычек (должна быть приятной)",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Показываем только приятные привычки для связанных
            self.fields["related_habit"].queryset = Habit.objects.filter(
                customer=user, is_pleasant=True
            )
            # Добавляем пустой вариант
            self.fields["related_habit"].empty_label = "-----"

            # Если редактируем существующую привычку, исключаем её саму из связанных
            if self.instance and self.instance.pk:
                self.fields["related_habit"].queryset = self.fields[
                    "related_habit"
                ].queryset.exclude(pk=self.instance.pk)

    def clean_planned_duration(self):
        """Проверка времени выполнения (не больше 120 секунд)"""
        duration = self.cleaned_data.get("planned_duration")
        if duration and duration.total_seconds() > 120:
            raise forms.ValidationError(
                "Время выполнения не должно превышать 120 секунд (2 минуты)"
            )
        return duration

    def clean_period(self):
        """Проверка периодичности (1-7 дней)"""
        period = self.cleaned_data.get("period")
        if period and (period < 1 or period > 7):
            raise forms.ValidationError("Периодичность должна быть от 1 до 7 дней")
        return period

    def clean(self):
        """Проверка связей между полями"""
        cleaned_data = super().clean()
        reward = cleaned_data.get("reward")
        related_habit = cleaned_data.get("related_habit")
        is_pleasant = cleaned_data.get("is_pleasant")

        # Нельзя одновременно указывать награду и связанную привычку
        if reward and related_habit:
            raise forms.ValidationError(
                "Нельзя заполнять одновременно награду и связанную привычку. "
                "Выберите что-то одно."
            )

        # У приятной привычки не может быть награды или связанной привычки
        if is_pleasant and (reward or related_habit):
            raise forms.ValidationError(
                "У приятной привычки не может быть награды или связанной привычки"
            )

        # Связанная привычка должна быть приятной (это также проверяется в модели)
        if related_habit and not related_habit.is_pleasant:
            raise forms.ValidationError("Связанная привычка должна быть приятной")

        return cleaned_data


class TrackerForm(forms.ModelForm):
    """Форма для отметки выполнения привычки"""

    class Meta:
        model = Tracker
        fields = ["status", "actual_duration", "completed_date"]
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select"},
                choices=[(True, "Выполнено"), (False, "Не выполнено")],
            ),
            "actual_duration": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "HH:MM:SS (например, 00:02:00)",
                }
            ),
            "completed_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
        }
        labels = {
            "status": "Статус выполнения",
            "actual_duration": "Фактическое время выполнения",
            "completed_date": "Дата выполнения",
        }
        help_texts = {
            "actual_duration": "Сколько времени реально потратили (не обязательно)",
            "completed_date": "За какой день отмечаете выполнение",
        }

    def clean_completed_date(self):
        """Дата выполнения не может быть в будущем"""
        completed_date = self.cleaned_data.get("completed_date")
        if completed_date and completed_date > timezone.now().date():
            raise forms.ValidationError("Нельзя отметить выполнение в будущем")
        return completed_date


class HabitFilterForm(forms.Form):
    """Форма фильтрации привычек"""

    STATUS_CHOICES = [
        ("all", "Все"),
        ("pleasant", "Приятные"),
        ("useful", "Полезные"),
        ("public", "Публичные"),
        ("my", "Мои"),
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    is_public = forms.ChoiceField(
        choices=[("", "Все"), (True, "Опубликованы"), (False, "Не опубликованы")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Поиск по названию или действию...",
            }
        ),
    )
