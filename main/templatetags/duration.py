from django import template
from django.utils.translation import get_language

register = template.Library()

default_russian_days_name = {
    '1': 'день',
    '2': 'дня',
    '3': 'дня',
    '4': 'дня',
    '5': 'дней',
    '6': 'дней',
    '7': 'дней',
    '8': 'дней',
    '9': 'дней',
    '0': 'дней',
}

def duration_time_format(value):
    current_language = get_language()
    value = str(value)
    if current_language == 'ru':
        if len(value) <= 8:
            return value
        else:
            if ',' in value:
                day, time = value.split(',')
                day_number, day_word = day.split()
            else:
                day_number, time = value.split()
            if len(day_number) == 1:
                day_word = default_russian_days_name[day_number]
            else:
                day_word = default_russian_days_name[day_number[-1]]

            return f'{day_number} {day_word}, {time}'
    return value

register.filter('duration_time_format', duration_time_format)
