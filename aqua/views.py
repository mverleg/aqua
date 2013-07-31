
from aqua.functions.notification import notification_work as notification
from django.contrib.auth import authenticate, login as login_func, logout as logout_func
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from timeslot.models import Roster, RosterWorker


def stylez(request):
	return render(request, 'stylez.html')


@login_required
def workhome(request):
	rosters_all = Roster.objects.all().order_by('-start')
	rosters_user = []
	for roster in rosters_all:
		if RosterWorker.objects.filter(roster = roster, user = request.user):
			rosters_user.append(roster)
	rosters_avilabilities = filter(lambda r: r.state == 1, rosters_user)
	rosters_final = filter(lambda r: r.state == 4, rosters_user)
	return render(request, 'workhome.html', {
		'user': request.user,
		'availabilities': rosters_avilabilities,
		'final': rosters_final,
	})


def login(request):
	#print 'request.GET: %s' % request.GET.get('next')
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login_func(request, user)
				if request.GET.get('next', ''):
					return redirect(to = request.POST.get('next', ''))
				else:
					return redirect(to = '/')
			else:
				return notification(request, 'Gebruikeraccount is uitgeschakeld')
		else:
			return notification(request, 'Geen geldige inloggegevens')
	else:
		return render(request, 'login_template.html', {
			'next': request.GET.get('next', ''),
		})


def logout(request):
	logout_func(request)
	if request.GET.get('next', ''):
		return redirect(to = request.POST.get('next', ''))
	else:
		return redirect(to = '/')


@login_required
def change_password(request):
	if request.method == 'POST':
		if not request.POST['new_password'] == request.POST['repeat_password']:
			return notification(request, 'De opgegeven nieuwe wachtwoorden zijn niet gelijk', next_page = reverse('change_password'))
		if not request.user.check_password(request.POST['current_password']):
			return notification(request, 'Dit is niet je huidige wachtwoord', next_page = reverse('change_password'))
		request.user.set_password(request.POST['new_password'])
		return notification(request, 'Je wachtwoord is veranderd', next_page = reverse('home'))
	else:
		return render(request, 'change_password.html')
