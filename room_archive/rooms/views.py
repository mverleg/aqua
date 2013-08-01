
from django.shortcuts import render
from rooms.models import Room, Style


def view_room(request, pk):
    
    try:
        room = Room.objects.get(pk = int(pk))
    except Room.DoesNotExist:
        room = None
    
    return render(request, 'view_room.html', {
        'room': room,
    })


def event_styles(request):
    response = render(request, 'event_styles.css', { 'styles': Style.objects.all() })
    response['Content-Type'] = 'text/css'
    return response

