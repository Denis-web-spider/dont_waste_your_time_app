from rest_framework import serializers
from rest_framework.serializers import ValidationError

from django.utils.translation import gettext as _

from main.models import Projects, Activities, Tasks
from main.templatetags.projects import status

class ProjectsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if ret.get('activity'):
            ret['activity'] = Activities.objects.get(id=ret['activity']).title
        else:
            ret['activity'] = '-'

        ret['status'] = status(ret['status'])
        ret['total_time'] = ret['total_time'][1:]

        if not ret['finished']:
            ret['finished'] = '-'

        return ret

    class Meta:
        model = Projects
        fields = '__all__'

class TasksSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if ret.get('activity'):
            ret['activity'] = Activities.objects.get(id=ret['activity']).title
        else:
            ret['activity'] = '-'

        if ret.get('project'):
            ret['project'] = Projects.objects.get(id=ret['project']).title
        else:
            ret['project'] = '-'

        return ret

    def validate(self, data):
        start = data['start']
        end = data['end']
        date = data['date']
        user = data['user']

        valid, task_in_that_time = Tasks.objects.is_task_in_free_time(start, end, date, user)
        if not valid:
            raise ValidationError(_('Данное время занято') + f' {task_in_that_time.title}')
        return data

    class Meta:
        model = Tasks
        fields = '__all__'

class ActivitiesSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if ret.get('parent'):
            ret['parent'] = Activities.objects.get(id=ret['parent']).title
        else:
            ret['parent'] = '-'

        ret['total_time'] = ret['total_time'][1:]

        return ret

    class Meta:
        model = Activities
        fields = '__all__'
