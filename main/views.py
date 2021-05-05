from django.shortcuts import render, redirect, reverse

from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import (
    ActivitiesForm,
    ProjectsForm,
    TasksForm,
)
from .models import Activities, Projects, Tasks
from .utils import activities_list, HTMLPagination

from datetime import datetime
import logging

logger = logging.getLogger('general')

class HomePageView(View):

    def get(self, request):
        if request.user.is_authenticated:
            logger.info('User is authenticated')
            return render(request, 'home.html')
        else:
            logger.info('User is not authenticated')
            return render(request, 'home_not_authenticated.html')

class ActivitiesView(LoginRequiredMixin, View):
    def get(self, request):
        form = ActivitiesForm()
        activities_html_list = activities_list(request.user)
        activities = Activities.objects.activities(request.user)

        fields = Activities._meta.get_fields()
        exclude = [
            Activities._meta.get_field('id'),
            Activities._meta.get_field('is_parent'),
            Activities._meta.get_field('user'),
            Activities._meta.get_field('number'),
        ]
        fields = [field for field in fields if field not in exclude]
        fields = fields[3:]

        logger.debug(f'Projects.objects.projects: {activities}')
        logger.debug(f'fields: {fields}')

        paginator = Paginator(activities, 50)
        page_number = int(request.GET.get('page', '1'))
        page = paginator.page(page_number)
        html_pagination = HTMLPagination(page, 'projects')

        context = {
            'form': form,
            'activities_html_list': activities_html_list,
            'fields': fields,
            'activities': page,
            'html_pagination': html_pagination,
        }

        return render(request, 'activities.html', context)

    def post(self, request):
        logger.debug(f'request.POST: {request.POST}')
        user = request.user
        activities = activities_list(user)

        form = ActivitiesForm(request.POST)
        if form.is_valid():
            logger.debug(f'Form is valid, form.cleaned_data: {form.cleaned_data}')

            Activities.objects.create(
                title=form.cleaned_data['title'],
                color=form.cleaned_data['color'],
                parent=form.cleaned_data['parent'],
                user=user
            )

            messages.success(request, _(f'Вид деятельности "{form.cleaned_data["title"]}" успешно добавлен'))
            return redirect(reverse('activities'))
        else:
            logger.debug(f'Form is not valid, form.errors: {form.errors}')

        context = {
            'form': form,
            'activities': activities
        }
        return render(request, 'activities.html', context)

class ProjectsView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        form = ProjectsForm(user)
        projects = Projects.objects.projects(user)
        fields = Projects._meta.get_fields()
        exclude_fields = [
            Projects._meta.get_field('user'),
            Projects._meta.get_field('id'),
        ]
        fields = [field for field in fields if field not in exclude_fields]
        fields.pop(0)

        logger.debug(f'Projects.objects.projects: {projects}')
        logger.debug(f'fields: {fields}')

        paginator = Paginator(projects, 50)
        page_number = int(request.GET.get('page', '1'))
        page = paginator.page(page_number)
        html_pagination = HTMLPagination(page, 'projects')

        context = {
            'form': form,
            'projects': page,
            'fields': fields,
            'html_pagination': html_pagination,
        }
        return render(request, 'projects.html', context)

class TasksView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user

        current_time = datetime.now().time().isoformat(timespec='minutes')
        current_date = datetime.now().date().isoformat()
        initial_form_data = {
            'start': current_time,
            'end': current_time,
            'date': current_date,
        }

        form = TasksForm(user=user, initial=initial_form_data)

        fields_exclude = [
            Tasks._meta.get_field('user'),
            Tasks._meta.get_field('id'),
            Tasks._meta.get_field('ending_in_next_day'),
        ]
        fields = [field for field in Tasks._meta.get_fields() if field not in fields_exclude]
        fields.append(fields.pop(fields.index(Tasks._meta.get_field('duration'))))

        tasks = Tasks.objects.tasks(user=user)

        paginator = Paginator(tasks, 50)
        page_number = int(request.GET.get('page', '1'))
        page = paginator.page(page_number)
        html_pagination = HTMLPagination(page, 'tasks')

        context = {
            'form': form,
            'fields': fields,
            'tasks': page,
            'html_pagination': html_pagination
        }

        return render(request, 'tasks.html', context)
