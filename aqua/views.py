from django.http import HttpResponse
from django.template import Template, Context
from aqua.functions.notification import notification_work as notification
from django.contrib.auth import authenticate, login as login_func, logout as logout_func
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from timeslot.models import Roster, RosterWorker
from aqua.forms import UserForm
from django.views.decorators.http import require_POST


def robots_txt(request):
	return HttpResponse('''User-agent: *
Allow: /ical
Disallow: /''')

@login_required
def work_home(request):
	rosters_all = Roster.objects.all().order_by('-start')
	rosters_user = []
	for roster in rosters_all:
		if RosterWorker.objects.filter(roster = roster, user = request.user):
			rosters_user.append(roster)
	rosters_actives = [roster for roster in rosters_user if (roster.state in [1, 4] and roster.active_around_now)]
	rosters_avilabilities = filter(lambda r: r.state == 1, rosters_user)
	rosters_final = filter(lambda r: r.state == 4, rosters_user)
	return render(request, 'work_home.html', {
		'user': request.user,
		'actives': rosters_actives,
		'availabilities': rosters_avilabilities,
		'final': rosters_final,
	})


def login(request):
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
@require_POST
def change_password(request):
	if not request.POST['new_password'] == request.POST['repeat_password']:
		return notification(request, 'De opgegeven nieuwe wachtwoorden zijn niet gelijk', next_page = reverse('change_password'))
	if not request.user.check_password(request.POST['current_password']):
		return notification(request, 'Dit is niet je huidige wachtwoord', next_page = reverse('change_password'))
	request.user.set_password(request.POST['new_password'])
	request.user.save()
	return notification(request, 'Je wachtwoord is veranderd', next_page = reverse('home'))


@login_required
def account(request):
	form = UserForm(instance = request.user)
	return render(request, 'account.html', {
		'user': request.user,
		'form': form,
	})


@login_required
@require_POST
def account_submit(request):
	form = UserForm(request.POST, instance = request.user)
	if form.is_valid():
		form.save()
		return redirect(to = reverse('account'))
	else:
		return render(request, 'account.html', {
			'user': request.user,
			'form': form,
		})


