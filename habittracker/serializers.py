from rest_framework import serializers
from .models import Habit, Tracker


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор для привычек с валидацией"""

    class Meta:
        model = Habit
        fields = [
            "id",
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
            "last_sent",
        ]
        read_only_fields = ["id", "customer", "last_sent"]

    def validate_planned_duration(self, value):
        if value and value.total_seconds() > 120:
            raise serializers.ValidationError(
                "Время выполнения не должно превышать 120 секунд"
            )
        return value

    def validate_period(self, value):
        if value < 1 or value > 7:
            raise serializers.ValidationError(
                "Периодичность должна быть от 1 до 7 дней"
            )
        return value

    def validate(self, data):
        reward = data.get("reward")
        related_habit = data.get("related_habit")
        is_pleasant = data.get("is_pleasant")

        if reward and related_habit:
            raise serializers.ValidationError(
                "Нельзя заполнять одновременно награду и связанную привычку"
            )

        if is_pleasant and (reward or related_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть награды или связанной привычки"
            )

        if related_habit and not related_habit.is_pleasant:
            raise serializers.ValidationError("Связанная привычка должна быть приятной")

        return data


class HabitListSerializer(serializers.ModelSerializer):
    """Упрощённый сериализатор для списка"""

    class Meta:
        model = Habit
        fields = ["id", "name", "action", "time", "period", "is_pleasant", "is_public"]


class TrackerSerializer(serializers.ModelSerializer):
    """Сериализатор для трекера"""

    habit_name = serializers.CharField(source="habit.name", read_only=True)

    class Meta:
        model = Tracker
        fields = [
            "id",
            "habit",
            "habit_name",
            "status",
            "actual_duration",
            "completed_date",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]
