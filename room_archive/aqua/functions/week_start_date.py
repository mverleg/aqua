

'''  http://stackoverflow.com/questions/396913/in-python-how-do-i-find-the-date-of-the-first-monday-of-a-given-week '''
def week_start_date(year, week):
    d = date(year, 1, 1)
    delta_days = d.isoweekday() - 1
    delta_weeks = week
    if year == d.isocalendar()[0]:
        delta_weeks -= 1
    delta = timedelta(days=-delta_days, weeks=delta_weeks)
    return datetime.combine(d + delta, time())

