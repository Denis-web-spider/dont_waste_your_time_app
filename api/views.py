from django.utils.translation import gettext as _

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ProjectsSerializer, TasksSerializer, ActivitiesSerializer

from main.utils import activities_list
from main.models import Projects, Activities, Tasks

import logging

logger = logging.getLogger('general')

class ActivitiesAPIView(APIView):

    def post(self, request):
        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        data = request.POST.copy()
        data['user'] = request.user.id

        logger.debug(f'data: {data}')

        serializer = ActivitiesSerializer(data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            activity = serializer.save()
            activity_serialized = ActivitiesSerializer(activity)
            data = activity_serialized.data
            data['message'] = _('Вид деятельности успешно добавлен')
            data['activities_html_list'] = activities_list(request.user)
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            data['errors'] = serializer.errors
            return Response(data)

    def patch(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        activity_id = int(request.POST['activity_id'])
        activity = Activities.objects.get(id=activity_id)

        if activity.user != request.user:
            result = {
                'errors': {'user-errors': _('Этот вид деятельности не принадлежит данному пользователю')}
            }
            logger.debug("This activity is not current user's activity")
            return Response(result)

        data = request.POST.copy()
        data['user'] = request.user.id

        serializer = ActivitiesSerializer(activity, data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            activity = serializer.save()
            activity_serialized = ActivitiesSerializer(activity)
            data = activity_serialized.data
            data['message'] = _('Вид деятельности успешно обновлен')
            data['activities_html_list'] = activities_list(request.user)
            data['activities'] = list(map(lambda activity: {'text': activity.title, 'value': activity.id}, Activities.objects.activities(request.user)))
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            result = {
                'errors': serializer.errors
            }
            return Response(result)

    def delete(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        response = {}
        response['deleted'] = False

        activity_id = int(request.POST.get('activity_id', 0))
        if activity_id:
            activity = Activities.objects.get(id=activity_id)
            if activity.user == request.user:
                logger.debug("This project is current user's project")
                activity.delete()
                response['deleted'] = True
                response['message'] = _('Вид деятельности успешно удален')
                response['activities_html_list'] = activities_list(request.user)
                logger.debug('Activity is deleted')

                return Response(response)
            else:
                response['errors'] = {'user_error': _('Этот вид деятельности не принадлежит данному пользователю')}
                logger.debug("This activity is not current user's activity")

                return Response(response)

        response['errors'] = {'unknown_error': _('По каким-то неизвестным причинам нам не удалось удалить Ваш вид деятельности')}
        return Response(response)

class ProjectsAPIView(APIView):

    def post(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        data = request.POST.copy()
        data['user'] = request.user.id

        logger.debug(f'data: {data}')

        serializer = ProjectsSerializer(data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            project = serializer.save()
            project_serialized = ProjectsSerializer(project)
            data = project_serialized.data
            data['message'] = _('Проект успешно добавлен')
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            data['errors'] = serializer.errors
            return Response(data)

    def patch(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        project_id = int(request.POST['project_id'])
        project = Projects.objects.get(id=project_id)

        if project.user != request.user:
            result = {
                'errors': {'user-errors': _('Этот проект не принадлежит данному пользователю')}
            }
            logger.debug("This project is not current user's project")
            return Response(result)

        data = request.POST.copy()
        data['user'] = request.user.id

        serializer = ProjectsSerializer(project, data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            project = serializer.save()
            project_serialized = ProjectsSerializer(project)
            data = project_serialized.data
            data['message'] = _('Проект успешно обновлен')
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            result = {
                'errors': serializer.errors
            }
            return Response(result)

    def delete(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        response = {}
        response['deleted'] = False

        project_id = int(request.POST.get('project_id', 0))
        if project_id:
            project = Projects.objects.get(id=project_id)
            if project.user == request.user:
                logger.debug("This project is current user's project")
                project.delete()
                response['deleted'] = True
                response['message'] = _('Проект успешно удален')
                logger.debug('Project is deleted')

                return Response(response)
            else:
                response['errors'] = {'user_error': _('Этот проект не принадлежит данному пользователю')}
                logger.debug("This project is not current user's project")

                return Response(response)

        response['errors'] = {'unknown_error': _('По каким-то неизвестным причинам нам не удалось удалить Ваш проект')}
        return Response(response)

class TasksAPIView(APIView):

    def post(self, request):
        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        data = request.POST.copy()
        data['user'] = request.user.id

        logger.debug(f'data: {data}')

        serializer = TasksSerializer(data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            task = serializer.save()
            task_serialized = TasksSerializer(task)
            data = task_serialized.data
            data['message'] = _('Задача успешно добавлена')
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            data['errors'] = serializer.errors
            return Response(data)

    def patch(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        task_id = int(request.POST['task_id'])
        task = Tasks.objects.get(id=task_id)

        if task.user != request.user:
            result = {
                'errors': {'user-errors': _('Этота задача не принадлежит данному пользователю')}
            }
            logger.debug("This task is not current user's task")
            return Response(result)

        data = request.POST.copy()
        data['user'] = request.user.id
        data['task_id'] = task_id

        serializer = TasksSerializer(task, data=data)
        if serializer.is_valid():
            logger.debug(f'serializer is valid, serializer.validated_data: {serializer.validated_data}')
            task = serializer.save()
            task_serialized = TasksSerializer(task)
            data = task_serialized.data
            data['message'] = _('Задача успешно обновлена')
            return Response(data)
        else:
            logger.debug(f'serializer is not valid, serializer.errors: {serializer.errors}')
            result = {
                'errors': serializer.errors
            }
            return Response(result)

    def delete(self, request):

        logger.debug(f'request.user: {request.user}')
        logger.debug(f'request.POST: {request.POST}')

        response = {}
        response['deleted'] = False

        task_id = int(request.POST.get('task_id', 0))
        if task_id:
            task = Tasks.objects.get(id=task_id)
            if task.user == request.user:
                logger.debug("This task is current user's task")
                task.delete()
                response['deleted'] = True
                response['message'] = _('Задача успешно удален')
                logger.debug('Task is deleted')

                return Response(response)
            else:
                response['errors'] = {'user_error': _('Эта задача не принадлежит данному пользователю')}
                logger.debug("This task is not current user's task")

                return Response(response)

        response['errors'] = {'unknown_error': _('По каким-то неизвестным причинам нам не удалось удалить Вашу задачу')}
        return Response(response)
