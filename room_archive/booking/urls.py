
from django.conf.urls import patterns, url
from django.contrib import admin
from reservations.views import schedule, view_reservation
from people.views import view_person, subscribe_status, subscribe_confirm,\
    unsubscribe_confirm
from rooms.views import view_room, event_styles
from reservations.reserve import pick_time, pick_room, enter_email, enter_name, reservation_done,\
    enter_email_submit, enter_name_submit, reservation_process
from django.views.generic.simple import direct_to_template
from moderate.views import cancel_reservation, cancel_reservation_confirm,\
    reservation_memos, moderation_page, no_shows
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', schedule, name = 'schedule'),
    url(r'^(?P<year>[0-9]+)/(?P<week>[0-9]+)/$', schedule, name = 'schedule'),
    url(r'^person/(?P<pk>[0-9]+)/$', view_person, name = 'person'),
    url(r'^room/(?P<pk>[0-9]+)/$', view_room, name = 'room'),
    url(r'^reservation/(?P<pk>[0-9]+)/$', view_reservation, name = 'reservation'),
    url(r'^zaalwacht/$', moderation_page, name = 'moderation'),
    url(r'^memos/$', reservation_memos, name = 'reservation_memos'),
    url(r'^memos/(?P<year>[0-9]+)/(?P<day>[0-9]+)/$', reservation_memos, name = 'reservation_memos'),
    url(r'^no_shows/$', no_shows, name = 'no_shows'),
    url(r'^pick_time/$', pick_time, name = 'pick_time'),
    url(r'^pick_room/$', pick_room, name = 'pick_room'),
    url(r'^enter_email/$', enter_email, name = 'enter_email'),
    url(r'^enter_email/submit/$', enter_email_submit, name = 'enter_email_submit'),
    url(r'^enter_name/$', enter_name, name = 'enter_name'),
    url(r'^enter_name/submit/$', enter_name_submit, name = 'enter_name_submit'),
    url(r'^reservation_process/$', reservation_process, name = 'reservation_process'),
    url(r'^reservation_done/$', reservation_done, name = 'reservation_done'),
    url(r'^event_styles\.css$', event_styles, name = 'event_styles'),
    url(r'^visiting_hours/$', direct_to_template, {'template': 'visiting_hours.html'}, name = 'visiting_hours'),
    url(r'^cancel_reservation/(?P<token>[0-9a-zA-Z]+)/$', cancel_reservation, name = 'cancel_reservation'),
    url(r'^cancel_reservation/(?P<token>[0-9a-zA-Z]+)/confirm/$', cancel_reservation_confirm, name = 'cancel_reservation_confirm'),
    url(r'^subscibe/(?P<token>[0-9a-zA-Z]+)/$', subscribe_status, name = 'subscribe_status'),
    url(r'^subscibe/(?P<token>[0-9a-zA-Z]+)/on/$', subscribe_confirm, name = 'subscribe_confirm'),
    url(r'^subscibe/(?P<token>[0-9a-zA-Z]+)/off/$', unsubscribe_confirm, name = 'unsubscribe_confirm'),
)


