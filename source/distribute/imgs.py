
# needed in live mode only:
# http://stackoverflow.com/questions/5833623/mplconfigdir-error-in-matplotlib
from os import environ
environ['MPLCONFIGDIR'] = '/tmp/'
import matplotlib as mpl
mpl.use('Agg')
from numpy import array, polyfit
from matplotlib.pyplot import subplots
from timeslot.models import RosterWorker, Roster
from distribute.models import Assignment, Availability
from datetime import timedelta
from django.http.response import HttpResponse


def hour_dist_scatter(request, roster):
    roster = Roster.objects.get(name = roster)
    users = [user for user in generate_user_stats(roster) if user.assignment_duration > 0]
    avail = array([user.availability_duration for user in users])
    rec = array([user.assignment_duration for user in users])
    extra = array([user.extra_duration for user in users])
    
    cor = [max(val, 0) for val in rec - extra]
    fit_param = polyfit(avail, cor, 1)
    fit_val = fit_param[0] * array(sorted(avail)) + fit_param[1]
    
    fig, ax = subplots(figsize = (6, 5))
    ax.set_title('%s (slope %.3f)' % (roster.name, fit_param[0]))
    ax.plot(sorted(avail), fit_val, label = 'linear fit', color = 'blue')
    #ax.scatter(avail, rec, label = 'totaal', color = 'gray')
    ax.scatter(avail, cor, label = 'bonus cor.', color = 'red')
    ax.set_xlim([0., max(avail) * 1.1])
    ax.set_ylim([0., max(rec) * 1.1])
    ax.set_xlabel('beschikbaar')
    ax.set_ylabel('gekregen')
    ax.legend(loc = 'lower right')
    response = HttpResponse(content_type='image/png')
    fig.savefig(response, bbox_inches = 0)
    return response


def generate_user_stats(roster):
    users = []
    for worker in RosterWorker.objects.filter(roster = roster):
        user = worker.user
        user.extra_duration = worker.extra
        worker_assignments = Assignment.objects.filter(timeslot__roster = roster, user = user)
        worker_assignments_duration = sum([assignment.timeslot.duration for assignment in worker_assignments], timedelta())
        user.assignment_duration = worker_assignments_duration.days * 24.0 + worker_assignments_duration.seconds / 3600.0
        worker_availabilities = Availability.objects.filter(timeslot__roster = roster, user = user)
        worker_availabilities_duration = sum([assignment.timeslot.duration for assignment in worker_availabilities], timedelta())
        user.availability_duration = worker_availabilities_duration.days * 24.0 + worker_availabilities_duration.seconds / 3600.0
        users.append(user)
    return users

