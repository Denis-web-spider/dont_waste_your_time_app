from django.urls import path

from .views import (
    HomePageView,
    ActivitiesView,
    ProjectsView,
    TasksView,
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('activities/', ActivitiesView.as_view(), name='activities'),
    path('projects/', ProjectsView.as_view(), name='projects'),
    path('tasks/', TasksView.as_view(), name='tasks')
]
