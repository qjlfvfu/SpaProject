from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'habits', views.HabitViewSet, basename='habit')
router.register(r'trackers', views.TrackerViewSet, basename='tracker')
router.register(r'public', views.PublicHabitListView, basename='public')

urlpatterns = [
    path('', include(router.urls)),
]