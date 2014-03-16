from django.shortcuts import render
from reservations.models import Reservation
from aqua.functions.notification import notification
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from rooms.models import Room


''' Only with the email can someone know the token '''


def cancel_reservation(request, token):
    
    try:
        reservation = Reservation.objects.get(delete_code = token)
    except Reservation.DoesNotExist:
        return notification(request, message = 'De reservering is niet gevonden')
    
    if reservation.start < datetime.now():
        if reservation.end < datetime.now():
            return notification(request, message = 'De reservering is in het verleden')
        else:
            return notification(request, message = 'De reservering is ingekort')
    #TODO test
    
    return render(request, 'view_reservation.html', {
        'is_confirmation': False,
        'is_cancellation': True,
        'reservation': reservation,
    })


def cancel_reservation_confirm(request, token):
    
    try:
        reservation = Reservation.objects.get(delete_code = token)
    except Reservation.DoesNotExist:
        return notification(request, message = 'De reservering is niet gevonden')
    
    if reservation.is_cancelled:
        return notification(request, message = 'De reservering is reeds geannuleerd')
    else:
        reservation.cancelled = datetime.now()
        reservation.save()
    
    return notification(request, message = 'De reservering is geannuleerd', next_page = reverse('reservation', kwargs = {'pk': reservation.pk}))


@login_required
def reservation_memos(request, year = None, day = None):
    
    # datetime to yearday
    # datetime.now().timetuple().tm_year
    # datetime.now().timetuple().tm_yday
    # yearday to datetime
    
    if not year or not day:
        printday = datetime.today() + timedelta(days = 1)
        nextday = datetime.today() + timedelta(days = 2)
    else:
        printday = datetime(int(year), 1, 1) + timedelta(int(day) - 1)
        nextday = datetime(int(year), 1, 1) + timedelta(int(day) + 0)
    
    reservations = {}
    for room in Room.objects.all():
        reservations[room.name] = Reservation.active.filter(start__gt = printday, start__lt = nextday, room = room)
    
    return render(request, 'memos_print.html', {
        'date': printday,
        'reservations': reservations,
    })


@login_required
def moderation_page(request):
    
    date = {}
    year = {}
    day = {}
    current = datetime.now()
    for key in ['today', 'tomorrow', 'after']:
        while current.weekday() >= 6:
            current += timedelta(days = 1)
        date[key] = current
        year[key] = current.timetuple().tm_year
        day[key] = current.timetuple().tm_yday
        current += timedelta(days = 1)
    
    return render(request, 'moderation.html', {
        'year': year,
        'day': day,
        'date': date,
    })


@login_required
def no_shows(request):
    reservations = Reservation.objects.filter(no_show = True, start__gte = datetime.now() - timedelta(days = 14))
    return render(request, 'no_shows.html', {
        'reservations': reservations,
    })


