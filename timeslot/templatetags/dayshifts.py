
import datetime
from timeslot.models import DATEFORMAT, TimeSlot, Roster
from django.template.loader import render_to_string
from django.template.defaultfilters import register


def dayshifts(day, roster):
    date = datetime.datetime.strptime(day, DATEFORMAT)
    roster = Roster.objects.get(pk = int(roster))
    slots = TimeSlot.objects.filter(roster = roster).filter(start__gt = date, start__lt = date + datetime.timedelta(days = 1)).order_by('start')
    return render_to_string('dayshifts.html', {
        'slots': slots,
    })
    

def dayshiftcount(day, roster):
    date = datetime.datetime.strptime(day, DATEFORMAT)
    return TimeSlot.objects.filter(roster = roster).filter(start__gt = date, start__lt = date + datetime.timedelta(days = 1)).count()
    

def daylong(day):
    date = datetime.datetime.strptime(day, DATEFORMAT)
    return date.strftime('%A %d-%m-%Y')
    

register.filter('dayshifts', dayshifts)
register.filter('dayshiftcount', dayshiftcount)
register.filter('daylong', daylong)

