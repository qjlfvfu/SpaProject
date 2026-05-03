from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    HabitListView,
    HabitCreateView,
    HabitDetailView,
    HabitUpdateView,
    HabitDeleteView,
    TrackerCreateView,
    complete_habit,
)

# API роутеры
router = DefaultRouter()
router.register(r"habits", views.HabitViewSet, basename="habit")
router.register(r"trackers", views.TrackerViewSet, basename="tracker")
router.register(r"public", views.PublicHabitListView, basename="public")

app_name = "habits"

# Объединяем API и HTML маршруты
urlpatterns = [
    # API маршруты
    path("api/", include(router.urls)),
    # HTML маршруты (шаблоны)
    path("", HabitListView.as_view(), name="habit_list"),
    path("create/", HabitCreateView.as_view(), name="habit_create"),
    path("<int:pk>/", HabitDetailView.as_view(), name="habit_detail"),
    path("<int:pk>/update/", HabitUpdateView.as_view(), name="habit_update"),
    path("<int:pk>/delete/", HabitDeleteView.as_view(), name="habit_delete"),
    path("<int:pk>/complete/", complete_habit, name="habit_complete"),
    path("track/<int:pk>/", TrackerCreateView.as_view(), name="track_habit"),
]
