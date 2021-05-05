from django import template

from main.models import Projects

register = template.Library()

def status(value):
    STATUS_CHOICES = Projects.STATUS_CHOICES
    for status_choice in STATUS_CHOICES:
        if status_choice[0] == value:
            return status_choice[1]

register.filter('status', status)
