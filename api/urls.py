from django.urls import path

from .views import ProjectsAPIView, TasksAPIView, ActivitiesAPIView

urlpatterns = [
    path('projects/', ProjectsAPIView.as_view()),
    path('tasks/', TasksAPIView.as_view()),
    path('activities/', ActivitiesAPIView.as_view())
]
