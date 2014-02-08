
from django.core.management import call_command
from datetime import datetime, timedelta
from timeslot.models import TimeSlot, Roster
from distribute.models import Availability

'''
    simply export the json database
'''
def backup():
    timestr = datetime.today().strftime('%Y-%m-%d_%H-%M')
    with open('backups/%s.json' % timestr, 'w+') as fh:
        call_command('dumpdata', stdout = fh)

'''
    send an overview email for each roster with timeslots in the coming week
'''
def mail_week():
    for roster in Roster.objects.all():
        timeslots = TimeSlot.objects.filter(roster = roster, start__gt = datetime.today(), start__lt = timedelta(days = 7))
        if len(timeslots):
            availabilities = Availability.objects.filter(timeslot__in = timeslots)
            for availability in availabilities:
                print availability

if __name__ == '__main__':
    backup()
    mail_week()


