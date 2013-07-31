
import datetime
from django.shortcuts import render, redirect
from timeslot.forms import CreateRosterForm, TemplateRosterForm, TimeSlotForm
from django.core.urlresolvers import reverse
from aqua.functions.notification import notification_work as notification
from timeslot.models import Roster, TimeSlot, DATETIMEFORMAT, DATEFORMAT, RosterWorker,\
    TIMEFORMAT
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User


@staff_member_required
def start_roster(request):
    if request.method == 'POST':
        create_roster_form = CreateRosterForm(request.POST)
        template_roster_form = TemplateRosterForm(request.POST)
        if create_roster_form.is_valid() and template_roster_form.is_valid():
            roster = create_roster_form.save()
            template_roster = template_roster_form.cleaned_data['roster']
            if template_roster:
                day = datetime.timedelta(days = 1)
                offset = (roster.start - template_roster.start)
                offset += ((template_roster.start.weekday() - roster.start.weekday())  % 7) * day
                template_shifts = TimeSlot.objects.filter(roster = template_roster)
                transcribing = True
                while transcribing:
                    for tmp_shift in template_shifts:
                        if tmp_shift.start + offset > datetime.datetime.combine(roster.start, datetime.time()) and tmp_shift.end + offset < datetime.datetime.combine(roster.end + day, datetime.time()):
                            TimeSlot(roster = roster, start = tmp_shift.start + offset, end = tmp_shift.end + offset, degeneracy = tmp_shift.degeneracy).save()
                    if roster.end < template_roster.end + offset:
                        transcribing = False
                    else:
                        offset += template_roster.end - template_roster.start
                        while not (template_roster.start + offset).weekday() == template_roster.start.weekday():
                            offset += day
                template_workers = RosterWorker.objects.filter(roster = template_roster)
                for tmp_worker in template_workers:
                    RosterWorker(user = tmp_worker.user, roster = roster, extra = 0).save()
            return redirect(to = reverse('add_timeslots', kwargs = {'roster': roster.pk}))
    else:
        create_roster_form = CreateRosterForm()
        template_roster_form = TemplateRosterForm()
    
    return render(request, 'start_roster.html', {
        'create_roster_form': create_roster_form,
        'template_roster_form': template_roster_form,
    })
    

@staff_member_required
def add_timeslot(request, roster):
    roster = Roster.objects.get(pk = int(roster))
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    refday = roster.start
    days = []
    slots = {}
    
    while refday <= roster.end:
        refnext = refday + datetime.timedelta(days = 1)
        days.append(refday.strftime(DATEFORMAT))
        slots[refday.strftime(DATEFORMAT)] = TimeSlot.objects.filter(roster = roster).filter(start__gt = refday, start__lt = refnext).order_by('start')
        refday = refnext
    
    if request.method == 'POST':
        slot_form = TimeSlotForm(request.POST)
        if slot_form.is_valid():
            if slot_form.cleaned_data['date'] >= roster.start and slot_form.cleaned_data['date'] <= roster.end:
                start = datetime.datetime.combine(slot_form.cleaned_data['date'], slot_form.cleaned_data['start'])
                end =   datetime.datetime.combine(slot_form.cleaned_data['date'], slot_form.cleaned_data['end'])
                TimeSlot(roster = roster, start = start, end = end, degeneracy = slot_form.cleaned_data['people']).save()
                slot_form = TimeSlotForm(initial = {
                    'next_date': start.strftime(DATEFORMAT),
                    'next_start': end.strftime(TIMEFORMAT),
                    'next_end': (end + datetime.timedelta(hours = 2)).strftime(TIMEFORMAT),
                    #TODO: this doesn't work somehow...
                })
            else:
                return notification(request, 'Dit tijdslot duurt van %s tot %s. De ingevoerde dag, %s, valt hierf buiten.' % (roster.start.strftime(DATETIMEFORMAT), roster.end.strftime(DATETIMEFORMAT), slot_form.cleaned_data['date'].strftime(DATETIMEFORMAT)))
    else:
        slot_form = TimeSlotForm(initial = {'roster': roster})
    
    return render(request, 'add_slots.html', {
        'roster': roster,
        'days': days,
        'slotlist': slots,
        'slot_form': slot_form,
    })
    

@staff_member_required
def delete_timeslot(request, slot):
    slot = TimeSlot.objects.get(pk = int(slot))
    roster = slot.roster
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    slot.delete()
    return redirect(to = reverse('add_timeslots', kwargs = {'roster': roster.pk}))
    

@staff_member_required
def timeslots_copy_day(request, roster, date, to = None):
    dateobj = datetime.datetime.strptime(date, DATEFORMAT)
    oneday = datetime.timedelta(days = 1)
    roster = Roster.objects.get(pk = int(roster))
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    day_slots = TimeSlot.objects.filter(roster = roster).filter(start__gt = dateobj, start__lt = dateobj + oneday).order_by('start')
    to_days = []
    if to == None:
        return render(request, 'copy_slots.html', {
            'roster': roster,
            'date': date,
            'slots': day_slots,
            'weekday': dateobj.strftime('%A'),
        })
    elif to == 'samedays' or to == 'weekdays' or to == 'alldays':
        refday = roster.start
        while refday <= roster.end:
            if to == 'samedays':
                if refday.weekday() == dateobj.weekday():
                    to_days.append(refday)
            elif to == 'weekdays':
                if refday.weekday() <= 4:
                    to_days.append(refday)
            elif to == 'alldays':
                to_days.append(refday)
            refday += oneday
    elif to == 'nextday':
        to_days = [dateobj + oneday]
    else:
        return notification(request, 'This is not a valid copying option')
    for day in to_days:
        slotcount = TimeSlot.objects.filter(roster = roster).filter(start__gt = day, start__lt = day + oneday).count()
        if not slotcount:
            for slot in day_slots:
                start = datetime.datetime.combine(day, slot.start.time())
                end = datetime.datetime.combine(day, slot.end.time())
                TimeSlot(roster = roster, start = start, end = end, degeneracy = slot.degeneracy).save()
    return redirect(to = reverse('add_timeslots', kwargs = {'roster': roster.pk}))
    

@staff_member_required
def timeslots_empty_day(request, roster, date, to = None):
    roster = Roster.objects.get(pk = int(roster))
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    dateobj = datetime.datetime.strptime(date, DATEFORMAT)
    day_slots = TimeSlot.objects.filter(roster = roster).filter(start__gt = dateobj, start__lt = dateobj + datetime.timedelta(days = 1)).order_by('start')
    for slot in day_slots:
        slot.delete()
    return redirect(to = reverse('add_timeslots', kwargs = {'roster': roster.pk}))
    

@staff_member_required
def roster_users(request, roster):
    roster = Roster.objects.get(pk = int(roster))
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    users = User.objects.all()
    active_user_pks = map(lambda rw: rw.user.pk, RosterWorker.objects.filter(roster = roster))
    for user in users:
        if user.pk in active_user_pks:
            user.working = True
            user.extra = RosterWorker.objects.get(user = user, roster = roster).extra
        else:
            user.working = False
            user.extra = 0.0
    return render(request, 'add_users.html', {
        'users': users,
        'roster': roster,
    })
    

@require_POST
@staff_member_required
def roster_users_submit(request, roster):
    roster = Roster.objects.get(pk = int(roster))
    if roster.state > 0:
        return notification(request, 'Dit rooster is geblokkeerd omdat uren al verdeeld worden')
    RosterWorker.objects.filter(roster = roster).delete()
    hours = {}
    for key in request.POST.keys():
        if key[0:6] == 'extra_':
            upk = int(key[6:])
            try:
                hours[upk] = float(request.POST[key])
            except ValueError:
                pass
        if key[0:5] == 'user_':
            user = User.objects.get(pk = int(key[5:]))
            RosterWorker(user = user, roster = roster).save()
    for upk, extra in hours.items():
        user = User.objects.get(pk = upk)
        rosteruser = RosterWorker.objects.filter(user = user, roster = roster)
        if rosteruser:
            rosteruser[0].extra = extra
            rosteruser[0].save()
    return redirect(to = reverse('roster_users', kwargs = {'roster': roster.pk}))


@staff_member_required
def roster_overview(request):
    rosters = Roster.objects.all().order_by('start')
    return render(request, 'roster_overview.html', {
        'rosters': rosters,
    })


@staff_member_required
def delete_roster(request, roster):
    roster = Roster.objects.get(pk = int(roster))
    roster.delete()
    return redirect(to = reverse('roster_overview'))



