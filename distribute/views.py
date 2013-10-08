
from timeslot.models import Roster, RosterWorker, TimeSlot
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from aqua.functions.notification import notification_work as notification
from distribute.models import Availability, Assignment
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse
from aqua.functions.to_hours import to_hours
from subprocess import Popen, STDOUT
from aqua.functions.week_start_date import week_start_date
import os
import datetime
from django.db.models.aggregates import Count
from aqua.functions.group_by import group_by


@staff_member_required
def roster_lock(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if roster.state > 0:
        return notification(request, 'Dit rooster is al geblokkeerd')
    return render(request, 'roster_lock.html', {
        'roster': roster, 
    })
    

@staff_member_required
def invite_workers(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if roster.state > 1:
        return notification(request, 'Je kunt nog niet, of niet langer, mensen uitnodigen')
    
    workers = RosterWorker.objects.filter(roster = roster)
    
    if not workers:
        return notification(request, 'Voeg een of meer werkers toe')
    else:
        roster.state = 1
        roster.save()
    
    for worker in workers:
        availabilities = filter(lambda av: av.roster == roster, Availability.objects.filter(user = worker.user))
        if availabilities:
            worker.hours_entered = to_hours(reduce(lambda d1, d2: d1 + d2, map(lambda av: av.timeslot.duration, availabilities)))
        else:
            worker.hours_entered = 0
    
    base_url = 'http://' + request.META['HTTP_HOST']
    
    timedelta_total = roster.total_work_time
    hours_total = timedelta_total.days * 24 + timedelta_total.seconds / 3600
    
    return render(request, 'invite_workers.html', {
        'hours_total': hours_total,
        'hours_pp': round(hours_total / len(workers), 1),
        'roster': roster,
        'workers': workers,
        'base_url': base_url,
    })
    

'''
@login_required
def rosters_availabilities(request):
    rosters_qd = Roster.objects.all().order_by('start')
    rosters = []
    for roster in rosters_qd:
        if roster.state == 1 \
        and RosterWorker.objects.filter(roster = roster, user = request.user):
            rosters.append(roster)
    rosters = filter(lambda r: r.state == 1, rosters)
    if len(rosters) == 1:
        return redirect(to = reverse('availability', kwargs = {'roster': rosters[0].pk}))
    else:
        return render(request, 'rosters_availabilities.html', {
            'rosters': rosters,
        })
'''

@login_required
def availability(request, roster, year = None, week = None):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state == 1:
        return notification(request, 'Je kunt nog niet, of niet meer, je beschikbaarheid doorgeven') 
    
    if not RosterWorker.objects.filter(roster = roster, user = request.user):
        return notification(request, 'Je bent niet uitgenodigd voor dit rooster')
    
    if year == None or week == None:
        return redirect(to = reverse('availability', kwargs={'roster': roster.name, 'year': roster.start.year, 'week': roster.start.isocalendar()[1]}))
    else:
        year = int(year)
        week = int(week)
    if year < roster.start.year or (week < roster.start.isocalendar()[1] and year == roster.start.year):
        return redirect(to = reverse('availability', kwargs={'roster': roster.name, 'year': roster.start.year, 'week': roster.start.isocalendar()[1]}))
    if year > roster.end.year or (week > roster.end.isocalendar()[1] and year == roster.end.year):
        return redirect(to = reverse('availability', kwargs={'roster': roster.name, 'year': roster.end.year, 'week': roster.end.isocalendar()[1]}))
    
    monday = week_start_date(year, week)
    day = datetime.timedelta(days = 1)
    
    schedule = {
        'monday':  {'date': monday.strftime('%a %d %b'), 'name': 'monday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday, end__lt = monday + day)},
        'tuesday': {'date': (monday + day).strftime('%a %d %b'), 'name': 'tuesday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday + day, end__lt = monday + 2 * day)},
        'wednesday': {'date': (monday + 2 * day).strftime('%a %d %b'), 'name': 'wednesday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday + 2 * day, end__lt = monday + 3 * day)},
        'thursday': {'date': (monday + 3 * day).strftime('%a %d %b'), 'name': 'thursday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday + 3 * day, end__lt = monday + 4 * day)},
        'friday': {'date': (monday + 4 * day).strftime('%a %d %b'), 'name': 'friday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday + 4 * day, end__lt = monday + 5 * day)},
        'saturday': {'date': (monday + 5 * day).strftime('%a %d %b'), 'name': 'saturday', 'timeslots': TimeSlot.objects.filter(roster = roster, start__gt = monday + 5 * day, end__lt = monday + 6 * day)},
    }
    
    for schedule_day in schedule.values():
        for timeslot in schedule_day['timeslots']:
            if Availability.objects.filter(user = request.user, timeslot = timeslot).count():
                timeslot.available = True
            else:
                timeslot.available = False
    
    (next_year, next_week) = (monday + 7 * day).isocalendar()[0:2]
    (prev_year, prev_week) = (monday - 7 * day).isocalendar()[0:2]
    
    if prev_year < roster.start.year or (prev_week < roster.start.isocalendar()[1] and prev_year == roster.start.year):
        (prev_year, prev_week) = (None, None)
    if next_year > roster.end.year or (next_week > roster.end.isocalendar()[1] and next_year == roster.end.year):
        (next_year, next_week) = (None, None)
    
    ''' Get jump links to all the weeks '''
    start_monday = week_start_date(roster.start.year, roster.start.isocalendar()[1])
    end_monday = week_start_date(roster.end.year, roster.end.isocalendar()[1])
    oneweek = datetime.timedelta(days = 7)
    mondays = []
    day_k = start_monday
    while day_k <= end_monday:
        mondays.append({'name': day_k.strftime('%d %b'), 'is_this_week': monday == day_k, 'year': day_k.year, 'week': day_k.isocalendar()[1]})
        day_k += oneweek
    
    return render(request, 'availability.html', {
        'roster': roster, 
        'schedule': schedule,
        'year': year,
        'prev_year': prev_year,
        'next_year': next_year,
        'week': week,
        'prev_week': prev_week,
        'next_week': next_week,
        'mondays': mondays,
    })


@login_required
@require_POST
def availability_submit(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state == 1:
        return notification(request, 'Je kunt nog niet, of niet meer, je beschikbaarheid doorgeven')
    
    if not RosterWorker.objects.filter(roster = roster, user = request.user):
        return notification(request, 'Je bent niet uitgenodigd voor dit rooster')
    
    if request.POST['shifts']:
        shift_pks = map(int, request.POST['shifts'].split(';'))
    else:
        shift_pks = []
    
    year = int(request.POST['year'])
    week = int(request.POST['week'])
    monday = week_start_date(year, week)
    day = datetime.timedelta(days = 1)
    
    weekslots = TimeSlot.objects.filter(roster = roster, start__gt = monday, end__lt = monday + 7 * day)
    Availability.objects.filter(user = request.user, timeslot__pk__in = map(lambda sl: sl.pk, weekslots)).delete()
    
    for shift_pk in shift_pks:
        shift = TimeSlot.objects.get(pk = shift_pk)
        Availability(user = request.user, timeslot = shift).save()
    
    return redirect(to = reverse('availability', kwargs = {'roster': roster.name, 'year': year, 'week': week}))


@login_required
def availability_copy(request, roster, year, week):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state == 1:
        return notification(request, 'Je kunt nog niet, of niet meer, je beschikbaarheid doorgeven')
    
    year = int(year)
    week = int(week)
    if year < roster.start.year or (week < roster.start.isocalendar()[1] and year == roster.start.year) \
    or year > roster.end.year or (week > roster.end.isocalendar()[1] and year == roster.end.year):
        return notification('Geen valide week')
    
    monday = week_start_date(year, week)
    day = datetime.timedelta(days = 1)
    
    weekslots = TimeSlot.objects.filter(roster = roster, start__gt = monday, end__lt = monday + 7 * day)
    weekavailabilities = Availability.objects.filter(user = request.user, timeslot__pk__in = map(lambda sl: sl.pk, weekslots))
    
    weeks = 0 * day
    while monday + weeks >= datetime.datetime.combine(roster.start, datetime.time()):
        weeks -= 7 * day
    while monday + weeks <= datetime.datetime.combine(roster.end, datetime.time()):
        if not ((monday + weeks).isocalendar()[0] == year and (monday + weeks).isocalendar()[1] == week):
            weekslots = TimeSlot.objects.filter(roster = roster, start__gt = monday + weeks, end__lt = monday + weeks + 7 * day)
            Availability.objects.filter(user = request.user, timeslot__pk__in = map(lambda sl: sl.pk, weekslots)).delete()
        weeks += 7 * day
    
    for weekav in weekavailabilities:
        weeks = 0 * day
        while weekav.timeslot.start + weeks >= datetime.datetime.combine(roster.start, datetime.time()):
            weeks -= 7 * day
        while weekav.timeslot.end + weeks <= datetime.datetime.combine(roster.end, datetime.time()):
            ts_match = TimeSlot.objects.filter(roster = roster, start = weekav.timeslot.start + weeks, end = weekav.timeslot.end + weeks)
            if ts_match:
                if not Availability.objects.filter(user = request.user, timeslot = ts_match):
                    Availability(user = request.user, timeslot = ts_match[0]).save()
            weeks += 7 * day
    
    return redirect(to = reverse('availability', kwargs = {'roster': roster.name, 'year': year, 'week': week}))


@staff_member_required
def calculate_start(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state in [1, 3]:
        return notification(request, 'Je kunt nu geen berekening starten')
    roster.state = 2
    roster.save()
    
    command = ['nohup', 'python', 'manage.py', 'calculate_roster', '%d' % roster.pk]
    Popen(command, shell = False, stdout = open(os.devnull, 'w'), stderr = STDOUT, stdin = open(os.devnull, 'w'))
    
    return redirect(to = reverse('calculate_status', kwargs = {'roster': roster.name}))
    

@staff_member_required
def calculate_restart(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state == 2:
        return notification(request, 'Je kan niet herstarten als er geen berekening bezig is')
    roster.state = 1
    roster.save()
    return redirect(to = reverse('invite_workers', kwargs = {'roster': roster.name}))
    

@staff_member_required
def calculate_status(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state in [2, 3]:
        return notification(request, 'Dit rooster wordt op het moment niet verdeeld')
    return render(request, 'calculate_status.html', {
        'roster': roster
    })
    

@staff_member_required
def calculate_publish(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state  == 3:
        return notification(request, 'Dit rooster kan niet openbaar worden gemaakt')
    roster.state = 4
    roster.save()
    return redirect(to = reverse('final_roster', kwargs = {'roster': roster.name}))
    

@staff_member_required
def roster_stats(request, roster):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    #if not roster.state in [3, 4]:
    #    return notification(request, 'Alleen verdeelde roosters hebben statistische informatie')
    ''' Hours per person '''
    users = []
    for worker in RosterWorker.objects.filter(roster = roster):
        user = worker.user
        user.extra_duration = worker.extra
        worker_assignments = Assignment.objects.filter(timeslot__roster = roster, user = user)
        worker_assignments_duration = sum([assignment.timeslot.duration for assignment in worker_assignments], datetime.timedelta())
        user.assignment_duration = worker_assignments_duration.days * 24.0 + worker_assignments_duration.seconds / 3600.0
        worker_availabilities = Availability.objects.filter(timeslot__roster = roster, user = user)
        worker_availabilities_duration = sum([assignment.timeslot.duration for assignment in worker_availabilities], datetime.timedelta())
        user.availability_duration = worker_availabilities_duration.days * 24.0 + worker_availabilities_duration.seconds / 3600.0
        users.append(user)
    
    ''' Availability density (high complexity, N^4 or something) '''
    timeslots = TimeSlot.objects.filter(roster = roster)
    availabilities = group_by(Availability.objects.filter(timeslot__roster = roster), 'timeslot')
    oneday = datetime.timedelta(days = 1)
    day = roster.start
    while day < roster.end:
        if day.isoweekday() == 1:
            #print '%s is monday' % day
            first_monday = day
            break
    day_stats = []
    if first_monday:
        day = first_monday
        while day < first_monday + 7 * oneday:
            day_timeslots = [timeslot for timeslot in timeslots if timeslot.start.date() == day]
            day_stat = {
                'weekday': day.strftime("%a"),
                'timeslots_sets': [],
            }
            for reference_timeslot in sorted(day_timeslots, key = lambda slot: slot.start):
                ''' Find equivalent timeslots in other weeks '''
                equivalents = {
                    'first_timeslots': reference_timeslot,
                    'equivalent_timeslots': [],
                    'equivalent_availabilities_length': 0,
                }
                weekday = day
                while weekday < roster.end:
                    weekday_timeslots = [timeslot for timeslot in timeslots if timeslot.start.date() == weekday]
                    for weekday_timeslot in weekday_timeslots:
                        if weekday_timeslot.start.time() == reference_timeslot.start.time() and weekday_timeslot.end.time() == reference_timeslot.end.time():
                            equivalents['equivalent_timeslots'].append(weekday_timeslot)
                            equivalents['equivalent_availabilities_length'] += len(availabilities[weekday_timeslot])
                    weekday += 7 * oneday
                day_stat['timeslots_sets'].append(equivalents)
            day_stats.append(day_stat)
            day += oneday
    
    return render(request, 'roster_stats.html', {
        'roster': roster,
        'users': users,
        'day_stats': day_stats,
    })
    


