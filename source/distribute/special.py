
"""
	one-time (=ugly) code to redistribute only weeks >= 3
"""

from django.http import HttpResponse
from timeslot.models import TimeSlot, Roster
from distribute.models import Assignment
from datetime import date, datetime


cutdt = datetime(year = 2014, month = 02, day = 16, second = 0)


def special_base(request):
	if not request.user.username == 'mark':
		raise Exception('just...no.')

	normalroster = Roster.objects.get(name = '2013-14_k3')
	if normalroster.state >= 4:
		raise Exception('nope.')
	try:
		specialroster = Roster.objects.get(name = 'tmp_special_2013k3')
	except Roster.DoesNotExist:
		specialroster = Roster(name = 'tmp_special_2013k3', start = date.today(), end = date.today())
		specialroster.save()

	ts = TimeSlot.objects.filter(roster__name = normalroster)
	tsf = ts.filter(start__gt = cutdt)

	return normalroster, specialroster, tsf


def move_to(tsqs, roster):
	for ts in tsqs:
		ts.roster = roster
		ts.save()


def special_1(request):
	return 'expired'
	normalroster, specialroster, tsf = special_base(request)

	Assignment.objects.filter(timeslot__in = tsf).delete()

	move_to(TimeSlot.objects.filter(roster__name = normalroster, start__lt = cutdt), specialroster)

	return HttpResponse('hello world %d / %d' % (len(TimeSlot.objects.filter(roster__name = normalroster)),
	                                             len(TimeSlot.objects.filter(roster__name = normalroster))))


def special_2(request):
	return 'expired'
	normalroster, specialroster, tsf = special_base(request)

	move_to(TimeSlot.objects.filter(roster__name = specialroster), normalroster)

	return HttpResponse('bye world %d / %d' % (len(TimeSlot.objects.filter(roster__name = normalroster)),
	                                           len(TimeSlot.objects.filter(roster__name = normalroster))))



