from django.contrib import admin
from .models import Habit, Tracker


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ["name", "customer", "time", "period", "is_pleasant", "is_public"]
    list_filter = ["is_pleasant", "is_public", "period"]
    search_fields = ["name", "action"]
    readonly_fields = ["last_sent"]


@admin.register(Tracker)
class TrackerAdmin(admin.ModelAdmin):
    list_display = ["habit", "user", "completed_date", "status"]
    list_filter = ["status", "completed_date"]
    search_fields = ["habit__name", "user__email"]
