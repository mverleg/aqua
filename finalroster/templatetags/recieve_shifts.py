
from django import template
from distribute.models import Assignment
from django.template.loader import render_to_string
from django.middleware import csrf

register = template.Library()


''' Show a list of shifts that people want to give you '''
@register.simple_tag(name = 'recieve_shifts', takes_context = True)
def recieve_shifts(context, *args, **kwargs):
    if context['request'].user.is_authenticated():
        shifts_recieved = Assignment.objects.filter(fortrade = 3, giveto = context['request'].user)
        if len(shifts_recieved):
            return render_to_string('recieve_shifts.html', {
                'shifts': shifts_recieved,
                'csrf_token': csrf.get_token(context['request']), # Not a good system because tokenname could change, but fuck that
                'path': context['request'].get_full_path(),
                })
    return ''


