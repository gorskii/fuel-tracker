from django import template
from django.utils import timezone


register = template.Library()


@register.filter
def key(d, k):
    """ Get dictionary value by key """
    if k in d:
        return d[k]
    return None


@register.filter
def to_date(value: timezone.timedelta):
    """ Print timedelta in human readable format """
    days = value.days
    if value < timezone.timedelta(0):
        value *= -1
        days = value.days
        if days == 1:
            days = 0
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 4:
        suffix = 'дней'
    elif days == 1:
        suffix = 'день'
    else:
        suffix = 'дня'
    td = "{} {} {}:{:02}:{:02}".format(days, suffix, hours, minutes, seconds)
    if days == 0:
        td = "{}:{:02}:{:02}".format(hours, minutes, seconds)
    return td


@register.filter(name='abs')
def abs_filter(value):
    return abs(value)
