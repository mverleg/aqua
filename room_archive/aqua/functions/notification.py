
from django.shortcuts import render


def notification(request, message, next_page = None):
    if next_page == '/':
        if 'next' in request.GET:
            next_page=  request.GET['next']
        else:
            next_page = '/'
    return render(request, 'notification.html', {
        'message': message,
        'next_page': next_page,
    })

def notification_work(request, message, next_page = None):
    if not next_page:
		next_page = request.GET.get('next', '/')
    return render(request, 'notification_work.html', {
        'message': message,
        'next_page': next_page,
    })


