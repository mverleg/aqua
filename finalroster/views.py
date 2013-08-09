
import datetime
from timeslot.models import Roster, TimeSlot, DATEFORMAT, RosterWorker
from aqua.functions.notification import notification_work as notification
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from distribute.models import Assignment
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User, AnonymousUser
from finalroster.forms import TimeForm
from aqua.functions.week_start_date import week_start_date
from django.db.utils import IntegrityError


@login_required
def month_overview(request, user, year = None, month = None):
    try:
        user = User.objects.get(username = user)
    except User.DoesNotExist:
        return notification(request, 'Gebruiker met gebruikersnaam \'%s\' niet gevonden' % user)
    day = datetime.timedelta(days = 1)
    if year and month:
        year = int(year)
        month = int(month)
    else:
        year = datetime.datetime.today().year
        if datetime.datetime.today().day < 20:
            month = datetime.datetime.today().month
        else:
            month = (datetime.datetime.today() - day * 21).month
    
    refday = datetime.datetime(year = year, month = month, day = 1)
    hourlist = {}
    grand_total_hours = 0.0
    while refday.month == month:
        day_shifts = TimeSlot.objects.filter(start__gt = refday, end__lt = refday + day)
        total_hours = 0.0
        for slot in day_shifts:
            assignments = Assignment.objects.filter(user = user, timeslot = slot)
            for assignmnet in assignments:
                total_hours += assignmnet.timeslot.duration.seconds / 3600.0
        hourlist[refday.day] = {
            'date': refday.strftime(DATEFORMAT),
            'day': refday.strftime('%d'),
            'weekday': refday.strftime('%a'),
            'hours': total_hours,
        }
        grand_total_hours += total_hours
        refday += day
    
    return render(request, 'shift_overview.html', {
        'user': user,
        'hourlist': hourlist,
        'total': grand_total_hours,
        'month': month,
        'prev_month': month - 1 if month > 1 else 12,
        'next_month': (month % 12) + 1,
        'year': year,
        'prev_year': year if month > 1 else year - 1,
        'next_year': year if month < 12 else year +1,
    })
    

@login_required
def month_overview_all(request):
    users = User.objects.all()
    return render(request, 'shift_overview_all.html', {
        'users': users,
    })
    

def final_roster(request, roster, year = None, week = None):
    try:
        roster = Roster.objects.get(name = roster)
    except Roster.DoesNotExist:
        return notification(request, 'Er is geen rooster genaamd \'%s\' gevonden' % roster)
    if not roster.state == 4 and not (roster.state == 3 and request.user.is_staff):
        return notification(request, 'Dit rooster kan je op het moment niet bekijken')
    if year == None or week == None:
        if datetime.date.today() < roster.start:
            year = roster.start.year
            week = roster.start.isocalendar()[1]
        elif datetime.date.today() > roster.end:
            year = roster.end.year
            week = roster.end.isocalendar()[1]
        else:
            year = datetime.date.today().year
            week = datetime.date.today().isocalendar()[1]
        return redirect(to = reverse('final_roster', kwargs={'roster': roster.name, 'year': year, 'week': week}))
    else:
        year = int(year)
        week = int(week)
    if year < roster.start.year or (week < roster.start.isocalendar()[1] and year == roster.start.year):
        return redirect(to = reverse('final_roster', kwargs={'roster': roster.name, 'year': roster.start.year, 'week': roster.start.isocalendar()[1]}))
    if year > roster.end.year or (week > roster.end.isocalendar()[1] and year == roster.end.year):
        return redirect(to = reverse('final_roster', kwargs={'roster': roster.name, 'year': roster.end.year, 'week': roster.end.isocalendar()[1]}))
    
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
    
    (next_year, next_week) = (monday + 7 * day).isocalendar()[0:2]
    (prev_year, prev_week) = (monday - 7 * day).isocalendar()[0:2]
    
    if prev_year < roster.start.year or (prev_week < roster.start.isocalendar()[1] and prev_year == roster.start.year):
        (prev_year, prev_week) = (None, None)
    if next_year > roster.end.year or (next_week > roster.end.isocalendar()[1] and next_year == roster.end.year):
        (next_year, next_week) = (None, None)
    
    urls = {}
    urls['all'] = 'http://' + request.get_host() + reverse('ical_all')
    urls['trade'] = 'http://' + request.get_host() + reverse('ical_trade')
    if request.user.is_authenticated():
        urls['own'] = 'http://' + request.get_host() + reverse('ical_own', kwargs = {'user': request.user.username})
        urls['available'] = 'http://' + request.get_host() + reverse('ical_available', kwargs = {'user': request.user.username})
    
    user = AnonymousUser()
    if request.user.is_authenticated():
        if RosterWorker.objects.filter(user = request.user, roster = roster):
            user = request.user
    
    ''' Get jump links to all the weeks '''
    start_monday = week_start_date(roster.start.year, roster.start.isocalendar()[1])
    end_monday = week_start_date(roster.end.year, roster.end.isocalendar()[1])
    oneweek = datetime.timedelta(days = 7)
    mondays = []
    day_k = start_monday
    while day_k <= end_monday:
        mondays.append({'name': day_k.strftime('%d %b'), 'is_this_week': monday == day_k, 'year': day_k.year, 'week': day_k.isocalendar()[1]})
        day_k += oneweek
    
    return render(request, 'final_roster.html', {
        'user': user,
        'roster': roster, 
        'schedule': schedule,
        'year': year,
        'prev_year': prev_year,
        'next_year': next_year,
        'week': week,
        'prev_week': prev_week,
        'next_week': next_week,
        'urls': urls,
        'mondays': mondays,
    })
    

@login_required
def slot_info(request, slot):
    slot = TimeSlot.objects.get(pk = int(slot))
    if not slot.roster.state == 4:
        return notification(request, 'Dit rooster kan op het moment niet aangepast worden')
    assignments = Assignment.objects.filter(timeslot = slot)
    owner_shift = [assignment for assignment in assignments if assignment.user == request.user]
    owner_shift = owner_shift[0] if owner_shift else None
    
    return render(request, 'slot_info.html', {
        'user': request.user,
        'slot': slot,
        'roster': slot.roster,
        'owner_shift': owner_shift,
        'assignments': assignments,
    })
    

def assignment_redirect(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
    

@login_required
@require_POST
def assignment_submit(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if not assignment.timeslot.roster.state == 4:
        return redirect(to = reverse('final_roster', kwargs = {'roster': assignment.timeslot.roster.ok}))
        return notification(request, 'Dit rooster kan je op het moment niet aangepast worden')
    if not RosterWorker.objects.filter(user = request.user, roster = assignment.timeslot.roster):
        return notification(request, 'Je kan tijdens dit rooster niet werken (je account is niet toegevoegd)')
    if assignment.user.pk != request.user.pk:
        return notification(request, 'Je mag alleen je eigen shifts aanpassen')
    if 'action' in request.POST.keys():
        if request.POST['action'] == 'keep':
            assignment.fortrade = 0
            assignment.giveto = None
        elif request.POST['action'] == 'trade':
            assignment.fortrade = 1
            assignment.giveto = None
        elif request.POST['action'] == 'free':
            assignment.fortrade = 2
            assignment.giveto = None
        elif request.POST['action'] == 'gift':
            users = [worker.user for worker in RosterWorker.objects.filter(roster = assignment.timeslot.roster).exclude(pk = request.user.pk).order_by('user__first_name')]
            return render(request, 'gift_select_user.html', {
                'assignment': assignment,
                'slot': assignment.timeslot,
                'roster': assignment.timeslot.roster,
                'users': users,
                'staff': 0,
            })
        elif request.POST['action'] == 'split':
            return render(request, 'split_select_time.html', {
				'timeform': TimeForm(),
                'assignment': assignment,
                'slot': assignment.timeslot,
                'roster': assignment.timeslot.roster,
                'users': User.objects.exclude(pk = request.user.pk),
            })
        else:
            return notification(request, 'Action not recognized')
        assignment.save()
        return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
    else:
        return notification(request, 'Form not recognized')
    

@login_required
@require_POST
def assignment_submit_staff(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if not request.user.is_staff:
        return notification(request, 'Alleen beheerders mogen dit doen')
    if 'action' in request.POST.keys():
        if request.POST['action'] == 'transfer':
            users = [worker.user for worker in RosterWorker.objects.filter(roster = assignment.timeslot.roster).all()]
            return render(request, 'gift_select_user.html', {
                'assignment': assignment,
                'slot': assignment.timeslot,
                'roster': assignment.timeslot.roster,
                'users': users,
                'staff': 1,
            })
        elif request.POST['action'] == 'terminate':
            timeslot = assignment.timeslot
            if timeslot.degeneracy <= 1:
                roster_name = timeslot.roster.name
                timeslot.delete()
                return redirect(to = reverse('final_roster', kwargs = {'roster': roster_name, 'year': timeslot.year(), 'week': timeslot.week()}))
            else:
                assignment.delete()
                timeslot.degeneracy -= 1
                timeslot.save()
        else:
            return notification(request, 'Action not recognized')
        return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
    else:
        return notification(request, 'Form not recognized')
    

@login_required
@require_POST
def assignment_submit_staff_empty(request, timeslot):
    timeslot = TimeSlot.objects.get(pk = int(timeslot))
    if not request.user.is_staff:
        return notification(request, 'Alleen beheerders mogen dit doen')
    try:
        if Assignment.objects.filter(timeslot = timeslot).count() < timeslot.degeneracy:
            assignment = Assignment(user = request.user, timeslot = timeslot, note = 'assigned by %s' % request.user)
            assignment.save()
    except IntegrityError:
        return notification(request, 'Sorry, je kan geen shift toewijzen als je zelf een shift op dat moment hebt. Dit omdat het achter de schermen werkt door tijdelijk jou een shift te geven en die over te zetten. Geef dus tijdelijk even je eigen shift af (of geef hem meteen aan de betreffende persoon en claim dan de lege).', next_page = reverse('slot_info', kwargs = { 'slot': timeslot.pk }))
    users = [worker.user for worker in RosterWorker.objects.filter(roster = timeslot.roster)]
    return render(request, 'gift_select_user.html', {
        'assignment': assignment,
        'slot': timeslot,
        'roster': timeslot.roster,
        'users': users,
        'staff': 1,
        'was_empty': True,
    })

@login_required
@require_POST
def assignment_submit_add_degeneracy(request, timeslot):
    timeslot = TimeSlot.objects.get(pk = int(timeslot))
    if not request.user.is_staff:
        return notification(request, 'Alleen beheerders mogen dit doen')
    timeslot.degeneracy += 1
    timeslot.save()
    return redirect(to = reverse('slot_info', kwargs = { 'slot': timeslot.pk }))

@login_required
@require_POST
def assignment_submit_delete_empty(request, timeslot):
    timeslot = TimeSlot.objects.get(pk = int(timeslot))
    if request.user.is_staff:
        if timeslot.degeneracy <= 1:
            roster_name = timeslot.roster.name
            timeslot.delete()
            return redirect(to = reverse('final_roster', kwargs = {'roster': roster_name}))
        else:
            timeslot.degeneracy -= 1
            timeslot.save()
            return redirect(to = reverse('slot_info', kwargs = {'slot': timeslot.pk}))
    else:
        return notification(request, 'Action not recognized')
    

@login_required
@require_POST
def assignment_submit_split(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if not RosterWorker.objects.filter(user = request.user, roster = assignment.timeslot.roster) and not request.user.is_staff():
        return notification(request, 'Je kan tijdens dit rooster niet werken (je account is niet toegevoegd)')
    if 'splitting' in request.POST.keys():
        form = TimeForm(request.POST)
        if form.is_valid():
            time = form.cleaned_data['time']
            sd = assignment.timeslot.start
            minshiftlength = datetime.timedelta(minutes = 29, seconds = 59)
            splitat = datetime.datetime.combine(datetime.date(sd.year, sd.month, sd.day), time)
            ''' Is the remaining shift long enough? '''
            if splitat > assignment.timeslot.start + minshiftlength and splitat < assignment.timeslot.end - minshiftlength:
                ''' We need to split the timeslot (happens for everyone; better than simultaneous slots) '''
                prevend = assignment.timeslot.end
                assignment.timeslot.end = splitat
                assignment.timeslot.save()
                ''' Clone trick '''
                ts_old_pk = assignment.timeslot.pk
                assignment.timeslot.pk = None
                assignment.timeslot.start = splitat
                assignment.timeslot.end = prevend
                assignment.timeslot.save()
                ts_new_pk = assignment.timeslot.pk
                ''' Then we need to clone the assignments for everyone '''
                assignments = Assignment.objects.filter(timeslot__pk = ts_old_pk)
                if not len(assignments):
                    raise Exception('Impossible situation (that seems to happen anyway)')
                for cloneassignment in assignments:
                    cloneassignment.pk = None
                    cloneassignment.timeslot = assignment.timeslot
                    cloneassignment.save()
                #return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
                return render(request, 'split_confirm.html', {
                     'timeslot1': TimeSlot.objects.get(pk = ts_old_pk),
                     'timeslot2': TimeSlot.objects.get(pk = ts_new_pk),
                })
        return notification(request, 'De opgegeven tijd was niet geldig')
    else:
        return notification(request, 'Form not recognized')


@login_required
@require_POST
def assignment_submit_transfer(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if request.user.is_staff:
        if 'user' in request.POST.keys():
            user = User.objects.get(pk = int(request.POST['user']))
            if not RosterWorker.objects.filter(user = user, roster = assignment.timeslot.roster):
                return notification(request, 'Je kan tijdens dit rooster niet werken (je account is niet toegevoegd)')
            if Assignment.objects.filter(timeslot = assignment.timeslot, user = user):
                return notification(request, '%s heeft dan al een shift' % user, next_page = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
            assignment.user = user
            assignment.giveto = None
            assignment.fortrade = 0
            assignment.save()
            return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
        else:
            return notification(request, 'Form not recognized')
    else:
        return notification(request, 'Not authorized (not a staff member)')


@login_required
@require_POST
def assignment_submit_gift(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if request.user == assignment.user:
        if 'user' in request.POST.keys():
            user = User.objects.get(pk = int(request.POST['user']))
            if not RosterWorker.objects.filter(user = user, roster = assignment.timeslot.roster):
                return notification(request, '%s kan tijdens dit rooster niet werken (account is niet toegevoegd)' % user.get_full_name)
            if Assignment.objects.filter(timeslot = assignment.timeslot, user = user):
                return notification(request, '%s heeft dan al een shift' % user, next_page = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
            assignment.giveto = user
            assignment.fortrade = 3
            assignment.save()
            return redirect(to = reverse('slot_info', kwargs = {'slot': assignment.timeslot.pk}))
        else:
            return notification(request, 'Form not recognized')
    else:
        return notification(request, 'Not authorized (not your shift)')


@login_required
@require_POST
def assignment_trade_result(request, assignment):
    assignment = Assignment.objects.get(pk = int(assignment))
    if not assignment.giveto == request.user:
        return notification(request, 'You cannot accept a shift for someone else', next_page = request.POST['next']) 
    assignment.fortrade = 0
    if request.POST['accept'] == 'yes':
        assignment.user = assignment.giveto
        assignment.giveto = None
    assignment.save()
    return redirect(to = request.POST['next'])


@login_required
@require_POST
def assignment_submit_claim(request, timeslot):
    timeslot = TimeSlot.objects.get(pk = int(timeslot))
    assignments = Assignment.objects.filter(timeslot = timeslot)
    if not RosterWorker.objects.filter(user = request.user, roster = timeslot.roster):
        return notification(request, 'Je kan tijdens dit rooster niet werken (je account is niet toegevoegd)')
    if any(assignment.user == request.user for assignment in assignments):
        return notification(request, 'You already have a shift at this time', next_page = reverse('slot_info', kwargs = {'slot': '%s' % timeslot.pk}))
    if len(assignments) < timeslot.degeneracy:
        Assignment(user = request.user, timeslot = timeslot, note = 'shift unknown (originally empty)').save()
        return redirect(to = reverse('slot_info', kwargs = {'slot': '%s' % timeslot.pk}))
    else:
        for assignment in assignments:
            if assignment.fortrade == 2:
                assignment.fortrade = 0
                assignment.user = request.user
                assignment.save()
                return redirect(to = reverse('slot_info', kwargs = {'slot': '%s' % timeslot.pk}))
    return notification(request, 'There is no shift to claim (anymore)', next_page = reverse('slot_info', kwargs = {'slot': '%s' % timeslot.pk}))







