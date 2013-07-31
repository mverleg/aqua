
from django.shortcuts import render, redirect
from datetime import date, timedelta
from reservations.models import Reservation
from rooms.models import Room
from people.forms import EmailForm, NameForm
from people.models import Person
from django.core.urlresolvers import reverse
from reservations.functions import has_time, has_room, get_times, has_user,\
    get_user, get_room
from aqua.functions.notification import notification
import re
from django.template.loader import render_to_string
from aqua import settings
from django.core.mail.message import EmailMultiAlternatives
from smtplib import SMTPSenderRefused


''' Let user pick a date and time for the reservation '''
def pick_time(request):
    return render(request, 'pick_time.html', {
        'tomorrow': date.today() + timedelta(days = 1),
    })


''' Let user pick an available room for the reservation '''
@has_time
def pick_room(request):
    ''' Remove room arguments; we're selecting it here '''
    if 'room' in request.GET:
        return redirect(to = '%s?%s' % (request.path, '&'.join(map(lambda x: '%s=%s' % (x, request.GET[x]), filter(lambda x: x != 'room', request.GET)))))
    
    ''' Get times (their existence was checked by the decorator) '''
    (start, end) = get_times(request)
    
    ''' Get status on the rooms for this time '''
    reservations = Reservation.active.filter(start__lte = start, end__gte = end)
    unavailable_rooms = set(reservation.room for reservation in reservations)
    all_rooms = set(Room.objects.all())
    available_rooms = all_rooms - unavailable_rooms
    
    return render(request, 'pick_room.html', {
        'available_rooms': available_rooms,
        'unavailable_rooms': unavailable_rooms,
        'begin': start,
        'finish': end,
        'get': '?%s' % '&'.join(map(lambda x: '%s=%s' % (x, request.GET[x]), filter(lambda x: x != 'room', request.GET))),
    })


''' Let user pick an email address '''
@has_time
@has_room
def enter_email(request):
    
    form = EmailForm()
    
    return render(request, 'enter_email.html', {
        'email_form': form,
        'reservation': '&'.join(['%s=%s' % (a, b) for a, b in request.GET.items()]),
    })
    

def enter_email_submit(request):
    if request.method == 'POST':
        if 'reservation' in request.POST:
            get =  request.POST['reservation']
        else:
            return notification(request, message = 'Er is geen reserveringsdata gevonden')
        form = EmailForm(request.POST)
        if form.is_valid():
            user = Person.objects.filter(email = form.cleaned_data['email'])
            description = request.POST.get('description', None)
            if user:
                ''' An existing user; to the final page '''
                if user[0].name:
                    if description:
                        return redirect(to = '%s?%s&user=%s&descr=%s' % (reverse(reservation_process), get, user[0].pk, description))
                    else:
                        return redirect(to = '%s?%s&user=%s' % (reverse(reservation_process), get, user[0].pk))
                else:
                    if description:
                        return redirect(to = '%s?%s&user=%s&descr=%s' % (reverse(enter_name), get, user[0].pk, description))
                    else:
                        return redirect(to = '%s?%s&user=%s' % (reverse(enter_name), get, user[0].pk))
            else:
                ''' A new user; enter a name before going to final page '''
                user = Person(email = form.cleaned_data['email'])
                user.save()
                return redirect(to = '%s?%s&user=%s' % (reverse(enter_name), get, user.pk))
        else:
            return notification(request, message = 'Er is geen geldig e-mailadres opgegeven.', next_page = '%s?%s' % (reverse('enter_email'), get))
    else:
        return redirect(to = reverse('enter_email'))


@has_time
@has_room
@has_user
def enter_name(request):
    
    form = NameForm(instance = get_user(request))
    
    return render(request, 'enter_name.html', {
        'name_form': form,
        'reservation': '&'.join(['%s=%s' % (a, b) for a, b in request.GET.items()]),
    })


def enter_name_submit(request):
    if request.method == 'POST':
        if 'reservation' in request.POST:
            get =  request.POST['reservation']
        else:
            return notification(request, message = 'Er is geen reserveringsdata gevonden')
        match = re.search('user=([0-9]+)', get)
        uid = int(match.group(1))
        person = Person.objects.get(pk = uid)
        form = NameForm(request.POST, instance = person)
        if form.is_valid():
            form.save()
            return redirect(to = '%s?%s' % (reverse(reservation_process), get))
        else:
            return notification(request, message = 'Er is geen geldige naam opgegeven.', next_page = '%s?%s' % (reverse('enter_name'), get))
    else:
        return redirect(to = reverse('enter_name'))
    

@has_time
@has_room
@has_user
def reservation_process(request):
    (start, end) = get_times(request)
    room = get_room(request)
    person = get_user(request)
    reserv = Reservation(person = person, room = room, start = start, end = end)
    
    if 'descr' in request.GET:
        reserv.name = request.GET['descr']
    
    try:
        reserv.save()
    except Exception:
        return redirect(to = '%s?reservation=0' % reverse(reservation_done))
    
    html = render_to_string('confirmation_html.email', {
        'reservation': reserv,
        'user': person,
        'base_url': settings.SITE_BASE_URL,
    })
    plain = render_to_string('confirmation_plain.email', {
        'reservation': reserv,
        'user': person,
        'base_url': settings.SITE_BASE_URL,
    })
    subject = 'Reservering %s op %s' % (room, reserv.start.strftime('%m %b'))
    
    if person.confirmations:
        try:
            msg = EmailMultiAlternatives(subject, plain, settings.EMAIL_HOST_USER, [person.email])
            msg.attach_alternative(html, "text/html")
            msg.send()
        except SMTPSenderRefused:
            return notification(request, 'Er kon geen e-mail verstuurd worden, excuses voor het ongemak. Mogelijk is de reservering wel gelukt; u kunt dat hieronder controleren.', next_page = reverse('schedule'))
    
    return redirect(to = '%s?reservation=%s' % (reverse(reservation_done), reserv.pk))
    

def reservation_done(request):
    if 'reservation' in request.GET:
        reservation = None
        if int(request.GET['reservation']) > 0:
            try:
                reservation = Reservation.objects.get(pk = int(request.GET['reservation']))
            except Reservation.DoesNotExist:
                return notification(request, message = 'Er is iets misgegaan bij het maken van de reservering (de reservering bestaat niet), excuses voor het ongemak.</p><p>Je kan ook bij een van de zaalwachten reserveren.')
        
        return render(request, 'view_reservation.html', {
            'is_confirmation': True,
            'is_cancellation': False,
            'reservation': reservation,
        })
    else:
        return notification(request, message = 'Er is iets misgegaan bij het maken van de reservering (geen reservering gevonden), excuses voor het ongemak.</p><p>Je kan ook bij een van de zaalwachten reserveren.')
    


