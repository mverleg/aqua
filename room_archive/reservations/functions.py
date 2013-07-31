
from django.core.urlresolvers import reverse
from django.utils.datastructures import MultiValueDictKeyError
from aqua.functions.notification import notification
from datetime import date
import datetime
from aqua.functions.los_is_open import los_is_open
from rooms.models import Room
from people.models import Person



def has_time(function):
    from reservations.reserve import pick_time
    def wrap(request, *args, **kwargs):
        err = get_error_times(request)
        if err:
            return notification(request, err, reverse(pick_time))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__= function.__doc__
    wrap.__name__= function.__name__
    return wrap


def has_room(function):
    from reservations.reserve import pick_room
    def wrap(request, *args, **kwargs):
        err = get_error_room(request)
        if err:
            return notification(request, err, reverse(pick_room))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__= function.__doc__
    wrap.__name__= function.__name__
    return wrap


def has_user(function):
    from reservations.reserve import enter_email
    def wrap(request, *args, **kwargs):
        err = get_error_user(request)
        if err:
            return notification(request, err, reverse(enter_email))
        else:
            return function(request, *args, **kwargs)
    wrap.__doc__= function.__doc__
    wrap.__name__= function.__name__
    return wrap


def get_error_times(request):
    try:
        (date, start, end) = times_get_extract(request)
    except MultiValueDictKeyError:
        return 'Geen datum en/of tijd voor de reservering gevonden.'
    except ValueError:
        return 'De ingevoerde datum en/of tijd konden niet gelezen worden.'
    try:
        datetime.datetime(date[0], date[1], date[2], start[0], start[1])
        datetime.datetime(date[0], date[1], date[2], end[0], end[1])
    except IndexError:
        return 'De ingevoerde datum en/of tijd konden niet gelezen worden.'
    begin = datetime.datetime(date[0], date[1], date[2], start[0], start[1])
    finish = datetime.datetime(date[0], date[1], date[2], end[0], end[1])
    if begin < datetime.datetime.now():
        return 'De reservering valt in het verleden.'
    if finish < begin + datetime.timedelta(minutes = 30):
        return 'De eindtijd ligt voor of te snel na de begintijd.'
    if not los_is_open(begin) or not los_is_open(finish):
        return 'Het opgegeven moment van niet binnen de <a href="%s">openingstijden</a> van de Library of Science.' % reverse('visiting_hours')
    return ''


def times_get_extract(request):
    date =  map(int, request.GET['date'].split('-'))
    start = map(int, request.GET['start'].split(':'))
    end =   map(int, request.GET['end'].split(':'))
    return (date, start, end)


''' It is assumed that validity of times has been checked '''
def get_times(request):
    (date, start, end) = times_get_extract(request)
    begin = datetime.datetime(date[0], date[1], date[2], start[0], start[1])
    finish = datetime.datetime(date[0], date[1], date[2], end[0], end[1])
    return (begin, finish)


def get_error_room(request):
    if 'room' not in request.GET:
        return 'Er is geen geldige ruimte ingevoerd.'
    try:
        Room.objects.get(pk = request.GET['room'])
    except Room.DoesNotExist:
        return 'De gevraagde ruimte bestaat niet'
    return ''
    

''' It is assumed that validity of times has been checked '''
def get_room(request):
    return Room.objects.get(pk = request.GET['room'])


def get_error_user(request):
    if 'user' in request.GET:
        try:
            Person.objects.get(pk = int(request.GET['user']))
        except Person.DoesNotExist:
            return 'De opgegeven gebruiker (%s) bestaat niet' % request.GET['user']
        except ValueError:
            return 'Dit is geen gebruikersnummer (%s)' % request.GET['user']
    else:
        return 'Er is geen geldige gebruiker opgegeven'
    return ''


''' It is assumed that validity of user has been checked '''
def get_user(request):
    return Person.objects.get(pk = int(request.GET['user']))





