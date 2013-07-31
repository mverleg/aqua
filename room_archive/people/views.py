
from django.shortcuts import render
from people.models import Person
from aqua.functions.notification import notification


def view_person(request, pk):
    
    try:
        person = Person.objects.get(pk = int(pk))
    except Person.DoesNotExist:
        person = None
    
    print person.reservations.all()
    
    return render(request, 'view_person.html', {
        'person': person,
    })


def subscribe_status(request, token):
    
    try:
        person = Person.objects.get(email_token = token)
    except Person.DoesNotExist:
        return notification(request, message = 'Deze persoon bestaat niet')
    
    return render(request, 'subscribe_status.html', {
        'person': person,
    })


def subscribe_confirm(request, token):
    
    try:
        person = Person.objects.get(email_token = token)
    except Person.DoesNotExist:
        return notification(request, message = 'Deze persoon bestaat niet')
    
    person.confirmations = True
    person.save()
    
    return notification(request, message = 'Je krijgt voortaan bericht als je een ruimte reserveert')


def unsubscribe_confirm(request, token):
    
    try:
        person = Person.objects.get(email_token = token)
    except Person.DoesNotExist:
        return notification(request, message = 'Deze persoon bestaat niet')
    
    person.confirmations = False
    person.save()
    
    return notification(request, message = 'Je krijgt niet langer bericht als je een ruimte reserveert')



