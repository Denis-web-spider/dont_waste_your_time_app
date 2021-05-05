from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible

from datetime import date, time, datetime, timedelta

User = get_user_model()

class ActivitiesManager(models.Manager):

    def activities(self, user):
        return self.get_queryset().filter(user=user)

@deconstructible
class Activities(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Название активности'))
    color = models.CharField(max_length=7, verbose_name=_('Цвет'))
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='childs', verbose_name=_('Родитель'))
    total_time = models.DurationField(default=timedelta(), verbose_name=_('Потрачено времени'))
    is_parent = models.BooleanField(default=False, verbose_name=_('Является родителем'))
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    number = models.PositiveIntegerField(default=1, verbose_name=_('Номер ребенка'))

    objects = ActivitiesManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.parent:
            self.parent.is_parent = True
            self.parent.save()

            if self in self.parent.childs.all():
                self.number = self.parent.childs.count()
            else:
                self.number = self.parent.childs.count() + 1

        super().save(*args, **kwargs)

    def calculate_total_time(self):
        tasks = self.tasks.all()

        for task in tasks:
            self.total_time += timedelta(
                hours=task.duration.hour,
                minutes=task.duration.minute,
                seconds=task.duration.second,
            )

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
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=IN_PROGRESS, verbose_name=_('Статус'))
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE, verbose_name=_('Вид деятельности'), blank=True, null=True)
    total_time = models.DurationField(default=timedelta(), verbose_name=_('Потрачено времени'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Создан'))
    finished = models.DateTimeField(verbose_name=_('Закончен'), blank=True, null=True)

    objects = ProjectsManager()

    def __str__(self):
        return self.title

    def calculate_total_time(self):
        tasks = self.tasks.all()

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

    def is_task_in_free_time(self, start: time, end: time, task_date: date, user):
        previous_day = date(year=task_date.year, month=task_date.month, day=task_date.day - 1)
        tasks = self.tasks(user)
        tasks = list(tasks.filter(date=previous_day, ending_in_next_day=True)) + list(tasks.filter(date=task_date))

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
                    (task_start <= current_task_start <= task_end)
                    or
                    (task_start <= current_task_end <= task_end)
                    or
                    (current_task_start <= task_start <= current_task_end)
                    or
                    (current_task_start <= task_end <= current_task_end)
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

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.end < self.start:
            self.ending_in_next_day = True
        super().save(*args, **kwargs)
        if self.project:
            self.project.calculate_total_time()
        if self.activity:
            self.activity.calculate_total_time()

    class Meta:
        ordering = ['-date', '-end']
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
