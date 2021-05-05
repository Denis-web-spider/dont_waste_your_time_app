from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Activities, Projects, Tasks

class AdminActivities(admin.ModelAdmin):
    list_display = ('title', 'color', 'color_display', 'parent', 'number', 'user', 'total_time', 'is_parent')
    list_display_links = ('title', 'color', 'color_display', 'parent', 'number', 'user', 'total_time', 'is_parent')
    list_filter = ('is_parent', 'parent')
    search_fields = ('title', 'parent__title', 'user__email')
    ordering = ('title', 'parent', 'user__email', 'total_time',)

    @admin.display(description=_('(Цвет)'))
    def color_display(self, obj):
        style = f'''
            background-color: {obj.color};
            padding: 1px 15px;
            margin-left: 10px;
            border: 1px solid white;
        '''
        return mark_safe(f'<span style="{style}"></span>')

class AdminProjects(admin.ModelAdmin):
    list_display = ['title', 'status', 'activity', 'user', 'total_time', 'created', 'finished']
    list_display_links = ['title', 'status', 'activity', 'user', 'total_time', 'created', 'finished']
    search_fields = ['title', 'activity__title', 'user__email']
    list_filter = ['status', 'created', 'finished']
    ordering = ['title', 'status', 'activity', 'user', 'total_time', 'created', 'finished']

class AdminTasks(admin.ModelAdmin):
    list_display = ['title', 'user', 'project', 'activity', 'start', 'end', 'duration', 'date', 'ending_in_next_day']
    list_display_links = ['title', 'user', 'project', 'activity', 'start', 'end', 'duration', 'date', 'ending_in_next_day']
    search_fields = ['title', 'user__email', 'project__title', 'activity__title']
    list_filter = ['duration', 'date', 'ending_in_next_day']
    ordering = ['title', 'user', 'project', 'activity', 'start', 'end', 'duration', 'date', 'ending_in_next_day']

admin.site.register(Activities, AdminActivities)
admin.site.register(Projects, AdminProjects)
admin.site.register(Tasks, AdminTasks)
