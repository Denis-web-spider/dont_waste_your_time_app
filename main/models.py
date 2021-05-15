from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.utils import timezone

from datetime import date, time, datetime, timedelta

User = get_user_model()

class ActivitiesManager(models.Manager):

    def return_all_activity_childs(self, activity):
        if activity.is_parent:
            return [activity] + [self.return_all_activity_childs(child_activity) for child_activity in activity.childs.all()]
        else:
            return activity

    def return_one_list_from_many_nested(self, nested_list, target_list):
        if isinstance(nested_list, list):
            [self.return_one_list_from_many_nested(item, target_list) for item in nested_list]
        else:
             target_list.append(nested_list)

    def activities(self, user):
        result_list = []
        for parent in self.get_queryset().filter(user=user).order_by('parent').filter(parent=None):
            self.return_one_list_from_many_nested(self.return_all_activity_childs(parent), result_list)
        result_list = list(map(lambda activity: activity.id, result_list))
        result_list = list(map(lambda activity_id: self.get_queryset().filter(id=activity_id), result_list))

        return self.none().union(*result_list)


@deconstructible
class Activities(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название активности'))
    color = models.CharField(default='#000000', max_length=7, verbose_name=_('Цвет'))
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='childs', verbose_name=_('Родитель'))
    total_time = models.DurationField(default=timedelta(), verbose_name=_('Потрачено времени'))
    is_parent = models.BooleanField(default=False, verbose_name=_('Является родителем'))
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    number = models.PositiveIntegerField(default=1, verbose_name=_('Номер ребенка'))

    objects = ActivitiesManager()

    original_parent = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_parent = self.parent

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if list(self.childs.all()):
            self.is_parent = True
        else:
            self.is_parent = False
        if self.parent:
            if self in self.parent.childs.all():
                self.number = self.parent.childs.count()
            else:
                self.number = self.parent.childs.count() + 1

        super().save(*args, **kwargs)
        if self.parent:
            self.parent.calculate_total_time()
        if self.parent != self.original_parent:
            if self.original_parent:
                self.original_parent.calculate_total_time()
            self.original_parent = self.parent

    def delete(self, *args, **kwargs):
        parent = None
        if self.parent:
            parent = self.parent
        super().delete(*args, **kwargs)
        parent.calculate_total_time()

    def calculate_total_time(self):
        tasks = self.tasks.all()

        self.total_time = timedelta()
        for task in tasks:
            self.total_time += timedelta(
                hours=task.duration.hour,
                minutes=task.duration.minute,
                seconds=task.duration.second,
            )

        childs = self.childs.all()
        for child in childs:
            self.total_time += child.total_time

        self.save()

    class Meta:
        verbose_name = _('Вид деятельности')
        verbose_name_plural = _('Виды деятельности')

class ProjectsManager(models.Manager):
    def projects(self, user):
        return self.get_queryset().filter(user=user)

class Projects(models.Model):
    IN_PROGRESS = 'P'
    FINISHED = 'F'
    STATUS_CHOICES = [
        (IN_PROGRESS, _('В процессе')),
        (FINISHED, _('Завершено'))
    ]

    title = models.CharField(max_length=255, verbose_name=_('Название проекта'))
    color = models.CharField(default='#000000', max_length=7, verbose_name=_('Цвет'))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=IN_PROGRESS, verbose_name=_('Статус'))
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name=_('Вид деятельности'), blank=True, null=True)
    total_time = models.DurationField(default=timedelta(), verbose_name=_('Потрачено времени'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    finished = models.DateTimeField(verbose_name=_('Закончен'), blank=True, null=True)

    objects = ProjectsManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.FINISHED:
            self.finished = timezone.now()
        else:
            self.finished = None
        super().save(*args, **kwargs)

    def calculate_total_time(self):
        tasks = self.tasks.all()

        self.total_time = timedelta()

        for task in tasks:
            self.total_time += timedelta(
                hours=task.duration.hour,
                minutes=task.duration.minute,
                seconds=task.duration.second,
            )

        self.save()

    class Meta:
        ordering = ['-created']
        verbose_name = _('Проект')
        verbose_name_plural = _('Проекты')

class TasksManager(models.Manager):

    def tasks(self, user):
        return self.get_queryset().filter(user=user)

    def is_task_in_free_time(self, start: time, end: time, task_date: date, user, current_task_id=0):
        previous_day = date(year=task_date.year, month=task_date.month, day=task_date.day - 1)
        tasks = self.tasks(user)
        if current_task_id:
            tasks = self.none().union(tasks.filter(date=previous_day, ending_in_next_day=True), tasks.filter(date=task_date).exclude(id=current_task_id))
        else:
            tasks = self.none().union(tasks.filter(date=previous_day, ending_in_next_day=True), tasks.filter(date=task_date))

        current_task_start = datetime(
            year=task_date.year,
            month=task_date.month,
            day=task_date.day,
            hour=start.hour,
            minute=start.minute,
            second=start.second
        )
        if end > start:
            current_task_end = datetime(
                year=task_date.year,
                month=task_date.month,
                day=task_date.day,
                hour=end.hour,
                minute=end.minute,
                second=end.second
            )
        else:
            current_task_end = datetime(
                year=task_date.year,
                month=task_date.month,
                day=task_date.day + 1,
                hour=end.hour,
                minute=end.minute,
                second=end.second
            )

        for task in tasks:

            task_start = datetime(
                year=task.date.year,
                month=task.date.month,
                day=task.date.day,
                hour=task.start.hour,
                minute=task.start.minute,
                second=task.start.second
            )

            if task.ending_in_next_day:
                task_end = datetime(
                    year=task.date.year,
                    month=task.date.month,
                    day=task.date.day + 1,
                    hour=task.end.hour,
                    minute=task.end.minute,
                    second=task.end.second
                )
            else:
                task_end = datetime(
                    year=task.date.year,
                    month=task.date.month,
                    day=task.date.day,
                    hour=task.end.hour,
                    minute=task.end.minute,
                    second=task.end.second
                )

            if(
                    (task_start < current_task_start < task_end)
                    or
                    (task_start < current_task_end <= task_end)
                    or
                    (current_task_start < task_start < current_task_end)
                    or
                    (current_task_start < task_end <= current_task_end)
            ):
                return False, task

        return True, None

class Tasks(models.Model):

    title = models.CharField(max_length=255, verbose_name=_('Название задачи'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    project = models.ForeignKey(Projects, verbose_name=_('Проект'), on_delete=models.CASCADE, blank=True, null=True, related_name='tasks')
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name=_('Вид деятельности'), blank=True, null=True, related_name='tasks')
    start = models.TimeField(default=time(hour=0, minute=0, second=0), verbose_name=_('Начало'))
    end = models.TimeField(default=time(hour=0, minute=0, second=0), verbose_name=_('Конец'))
    duration = models.TimeField(default=time(hour=0, minute=0, second=0), verbose_name=_('Время'))
    date = models.DateField(default=date.today, verbose_name=_('Дата'))
    ending_in_next_day = models.BooleanField(default=False, verbose_name=_('Заканчивается на следующий день'))

    objects = TasksManager()

    original_project = None
    original_activity = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.activity:
            self.original_activity = self.activity
        if self.project:
            self.original_project = self.project

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.end < self.start:
            self.ending_in_next_day = True

        start_datetime = datetime(
            year=self.date.year,
            month=self.date.month,
            day=self.date.day,
            hour=self.start.hour,
            minute=self.start.minute,
            second=self.start.second
        )
        if self.ending_in_next_day:
            end_datetime = datetime(
                year=self.date.year,
                month=self.date.month,
                day=self.date.day + 1,
                hour=self.end.hour,
                minute=self.end.minute,
                second=self.end.second
            )
        else:
            end_datetime = datetime(
                year=self.date.year,
                month=self.date.month,
                day=self.date.day,
                hour=self.end.hour,
                minute=self.end.minute,
                second=self.end.second
            )

        duration_timedelta = end_datetime - start_datetime
        hour = int(str(duration_timedelta).split(':')[0])
        minute = int(str(duration_timedelta).split(':')[1])
        second = int(str(duration_timedelta).split(':')[2])
        self.duration = time(
            hour=hour,
            minute=minute,
            second=second,
        )

        super().save(*args, **kwargs)
        if self.project:
            self.project.calculate_total_time()

        if self.project != self.original_project:
            if self.original_project:
                self.original_project.calculate_total_time()
            self.original_project = self.project

        if self.activity:
            self.activity.calculate_total_time()

        if self.activity != self.original_activity:
            if self.original_activity:
                self.original_activity.calculate_total_time()
            self.original_activity = self.activity

    def delete(self, *args, **kwargs):
        project = None
        activity = None
        if self.project:
            project = self.project
        if self.activity:
            activity = self.activity

        super().delete(*args, **kwargs)

        if project:
            project.calculate_total_time()
        if activity:
            activity.calculate_total_time()

    class Meta:
        ordering = ['-date', '-start']
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
