
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from icalendar import Calendar
from aqua.functions.notification import notification
from tex_response import render_pdf
from timeslot.models import TimeSlot, DATEFORMAT
from distribute.models import Assignment
from django.contrib.auth import get_user_model
from urllib2 import urlopen


DAY_NAMES = ('maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag')
MONTH_NAMES = ('', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december')


def overview_context(user, year, month):
	day = timedelta(days = 1)
	refday = datetime(year = year, month = month, day = 1)
	hourlist = {}
	grand_total_hours = 0.
	while refday.month == month:
		day_shifts = TimeSlot.objects.filter(start__gt = refday, end__lt = refday + day)
		total_hours = 0.
		for slot in day_shifts:
			assignments = Assignment.objects.filter(user = user, timeslot = slot)
			for assignmnet in assignments:
				total_hours += assignmnet.timeslot.duration.seconds / 3600.
		rounded_hours = '%d:%.2d' % (total_hours // 1, 15 * round((total_hours % 1) / .25)) if total_hours else None
		hourlist[refday.day] = {
			'date': refday.strftime(DATEFORMAT),
			'day': refday.strftime('%d'),
			'weekday': DAY_NAMES[refday.weekday()],
			'hours': rounded_hours,
		}
		grand_total_hours += total_hours
		refday += day
	return {
		'user': user,
		'hourlist': hourlist,
		'total': '%d:%.2d' % (grand_total_hours // 1, 15 * round((grand_total_hours % 1) / .25)),
		'month_name': MONTH_NAMES[month],
		'month': month,
		'prev_month': month - 1 if month > 1 else 12,
		'next_month': (month % 12) + 1,
		'year': year,
		'prev_year': year if month > 1 else year - 1,
		'next_year': year if month < 12 else year +1,
	}


def work_hour_pdf(request, year, month, user, template = 'werkbriefje.tex'):
	try:
		user = get_user_model().objects.get(username = user)
	except User.DoesNotExist:
		return notification(request, 'Gebruiker met gebruikersnaam \'%s\' niet gevonden' % user)
	day, today = timedelta(days = 1), datetime.today()
	if year and month:
		year = int(year)
		month = int(month)
	else:
		year = today.year
		if today.day < 20:
			month = today.month
		else:
			month = (today - day * 21).month
	context = overview_context(user, year, month)
	context.update({
		'date': '%s %s %s %s' % (DAY_NAMES[today.weekday()], today.day, MONTH_NAMES[today.month], today.year),
		'birthday': '%s %s %s' % (user.birthday.day, MONTH_NAMES[user.birthday.month], user.birthday.year) if user.birthday else '',
	})
	return render_pdf(request, template, context, filename = '%s_%.4d_%s.pdf' % (request.user.username, year, MONTH_NAMES[month]))


roomfeeds = [
	('HG00.208', 'https://www.google.com/calendar/ical/5j2r2l4nk8cv0nk9l8sphtj2ek%40group.calendar.google.com/private-0b8e22e03be5f1b351edf010fa32d10e/basic.ics'),
	('HG00.209', 'https://www.google.com/calendar/ical/rooj6j242gar457dpgn31nimvo%40group.calendar.google.com/private-29c8ce32290a9eda91f983d66d772f14/basic.ics'),
	('HG00.210', 'https://www.google.com/calendar/ical/hh4vu9s9qbvinsvntfg38tgojg%40group.calendar.google.com/private-ad634e31d71ec00004a545a02b402850/basic.ics'),
	('HG00.211', 'https://www.google.com/calendar/ical/c8hmlh5gerg0j4ci61vbj96teg%40group.calendar.google.com/private-62702d3f516546884a4134501f6900e3/basic.ics'),
	('HG00.212', 'https://www.google.com/calendar/ical/qagg0v2voc14tnov2hvf04bjdk%40group.calendar.google.com/private-0f7df89d9cb95318b4f50943e6913fcc/basic.ics'),
	('HG00.213', 'https://www.google.com/calendar/ical/nbfdq9h931hv6me893h0s3c5ec%40group.calendar.google.com/private-425fdcd83591e018ebb8f7a9a6a6cd51/basic.ics'),
	('HG00.214', 'https://www.google.com/calendar/ical/g9vu0jmq9upo9547n52a0sg3ts%40group.calendar.google.com/private-2a8f8bab3513e48e79549d5d45d8484e/basic.ics'),
	('HG00.215', 'https://www.google.com/calendar/ical/f5ivnilje8dgrpkg16pvsicsg0%40group.calendar.google.com/private-757e5a51d44b041de87d7869abbb439b/basic.ics'),
	('HG00.216', 'https://www.google.com/calendar/ical/r24p6sv0vlcglha4e6da6mbiqk%40group.calendar.google.com/private-1883280dfbde82739ccbdea9dd224ea0/basic.ics'),
]


def zaal_briefjes(request, year = None, month = None, day = None):
	if year is None or month is None or day is None:
		date = datetime.now() + timedelta(days = 1)
		return redirect(to = reverse('room_reservations', kwargs = {
			'year': '%.4d' % date.year,
			'month': '%.2d' % date.month,
			'day': '%.2d' % date.day
		}))
	year, month, day = int(year), int(month), int(day)
	thisday = datetime(year = year, month = month, day = day)
	bookings = []
	for room, url in roomfeeds:
		bookings.append({
			'room': room,
			'date': thisday.strftime('%A %d %B'),
			'items': [],
		})
		cal = Calendar.from_ical(urlopen(url).read())
		for event in cal.walk('vevent'):
			date = event.get('dtstart').dt
			if date.year == year and date.month == month and date.day == day:
				bookings[-1]['items'].append({
					'start': event.get('dtstart').dt.strftime('%H:%M'),
					'end': event.get('dtend').dt.strftime('%H:%M'),
					'text': unicode(event.get('summary')),
				})
		bookings[-1]['items'] = sorted(bookings[-1]['items'], key = lambda event: event['start'])
	return render_pdf(request, 'zaalreserveringen.tex', {
		'bookings': bookings,
	}, filename = 'room_reservations_%.4d_%.2d_%.2d.pdf' % (year, month, day))


