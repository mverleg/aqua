
from django.shortcuts import render
from reservations.models import Reservation
from datetime import date, timedelta, datetime, time


def schedule(request, year = None, week =  None):
    
    if year == None:
        year = date.today().year
    else:
        year =  int(year)
    
    if week == None:
        week = date.today().isocalendar()[1]
    else:
        week =  int(week)
    
    monday = week_start_date(year, week)
    day = timedelta(days = 1)
    
    schedule = {
        'monday':  {'date': monday.strftime('%a %d %b'), 'name': 'monday', 'reservations': Reservation.active.filter(start__gt = monday, end__lt = monday + day)},
        'tuesday': {'date': (monday + day).strftime('%a %d %b'), 'name': 'tuesday', 'reservations': Reservation.active.filter(start__gt = monday + day, end__lt = monday + 2 * day)},
        'wednesday': {'date': (monday + 2 * day).strftime('%a %d %b'), 'name': 'wednesday', 'reservations': Reservation.active.filter(start__gt = monday + 2 * day, end__lt = monday + 3 * day)},
        'thursday': {'date': (monday + 3 * day).strftime('%a %d %b'), 'name': 'thursday', 'reservations': Reservation.active.filter(start__gt = monday + 3 * day, end__lt = monday + 4 * day)},
        'friday': {'date': (monday + 4 * day).strftime('%a %d %b'), 'name': 'friday', 'reservations': Reservation.active.filter(start__gt = monday + 4 * day, end__lt = monday + 5 * day)},
        'saturday': {'date': (monday + 5 * day).strftime('%a %d %b'), 'name': 'saturday', 'reservations': Reservation.active.filter(start__gt = monday + 5 * day, end__lt = monday + 6 * day)},
    }
    
    (next_year, next_week) = (monday + 7 * day).isocalendar()[0:2]
    (prev_year, prev_week) = (monday - 7 * day).isocalendar()[0:2]
    
    return render(request, 'reservations.html', {
        'schedule': schedule,
        'year': year,
        'prev_year': prev_year,
        'next_year': next_year,
        'week': week,
        'prev_week': prev_week,
        'next_week': next_week,
    })



def view_reservation(request, pk):
    
    try:
        reservation = Reservation.objects.get(pk = int(pk))
    except Reservation.DoesNotExist:
        reservation = None
    
    return render(request, 'view_reservation.html', {
        'is_confirmation': False,
        'is_cancellation': False,
        'reservation': reservation,
    })
    




