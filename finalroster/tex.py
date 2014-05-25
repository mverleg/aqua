
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from aqua.functions.notification import notification
from tex_response import render_pdf
from timeslot.models import TimeSlot, DATEFORMAT
from distribute.models import Assignment
from django.contrib.auth import get_user_model


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
    return render_pdf(request, template, context, filename = '%s_%.4d_%s.pdf' % (request.user, year, MONTH_NAMES[month]))


