
from datetime import datetime, timedelta
from timeslot.models import TimeSlot, Roster
from distribute.models import Assignment
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from settings import EMAIL_HOST_USER


class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'For each roster, mail an overview of assignments for the next week'
    
    def handle(self, *args, **options):
        header = 'backup %s' % datetime.today().strftime('%Y-%m-%d %H:%M')
        body = 'overview of the next two weeks\n\n'
        for roster in Roster.objects.all():
            timeslots = TimeSlot.objects.filter(roster = roster, start__gt = datetime.today(), start__lt = (datetime.today() + timedelta(days = 14)))
            if len(timeslots):
                assignments = Assignment.objects.filter(timeslot__in = timeslots)
                body += '%s\n\n' % (roster.name)
                body += '\n'.join('%s-%s: %s (%s)' % (assignment.timeslot.start.strftime('%Y-%m-%d %H:%M'), assignment.timeslot.end.strftime('%H:%M'), assignment.user.get_full_name(), assignment.user.username) for assignment in assignments)
                send_mail(header, body, EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently = False)


