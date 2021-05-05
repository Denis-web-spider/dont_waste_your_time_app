from django.utils.translation import gettext as _

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import ProjectsSerializer, TasksSerializer, ActivitiesSerializer

from main.utils import activities_list

import logging

logger = logging.getLogger('general')

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
