
from django.conf.urls import patterns, url, include
from django.contrib import admin
from aqua.views import login, logout, change_password, work_home
from timeslot.views import start_roster, add_timeslot, delete_timeslot,\
    timeslots_copy_day, timeslots_empty_day, roster_users, roster_overview,\
    delete_roster, roster_users_submit
from distribute.views import roster_lock, invite_workers, availability,\
    availability_submit, availability_copy, calculate_start, \
    calculate_status, calculate_publish, calculate_restart, roster_stats
from finalroster.views import final_roster, slot_info, assignment_submit,\
    assignment_trade_result, month_overview, month_overview_all,\
    assignment_submit_split, assignment_submit_gift, assignment_submit_claim,\
    assignment_submit_staff, assignment_submit_transfer,\
    assignment_submit_delete_empty, assignment_submit_staff_empty,\
    assignment_submit_add_degeneracy, assignment_redirect, all_rosters_txt,\
    ical_html_all
from finalroster.calendar import AllCalendar, OwnCalendar, TradeCalendar,\
    AvailableCalendar
from distribute.imgs import hour_dist_scatter
from distribute.special import special_1, special_2
admin.autodiscover()


urlpatterns = patterns('',
	url(r'^special/1/', special_1),
	url(r'^special/2/', special_2),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^login/$', login, name='login'),
	url(r'^logout/$', logout, name='logout'),
    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^$', work_home, name = 'home'),
    url(r'^show/txt/$', all_rosters_txt, name = 'all_rosters_txt'),
    url(r'^show/txt/(?P<year>[0-9]+)/(?P<week>[0-9]+)/$', all_rosters_txt, name = 'all_rosters_txt'),
    url(r'^show/(?P<roster>[^/]+)/$', final_roster, name = 'final_roster'),
    url(r'^show/(?P<roster>[^/]+)/(?P<year>[0-9]+)/(?P<week>[0-9]+)/$', final_roster, name = 'final_roster'),
    url(r'^roster/$', start_roster, name = 'start_roster'),
    url(r'^roster/overview/$', roster_overview, name = 'roster_overview'),
    url(r'^roster/(?P<roster>[^/]+)/delete/$', delete_roster, name = 'delete_roster'),
    url(r'^roster/(?P<roster>[^/]+)/slots/$', add_timeslot, name = 'add_timeslots'),
    url(r'^roster/(?P<roster>[^/]+)/copy_day/(?P<date>\d{4}-\d{2}-\d{2})/$', timeslots_copy_day, name = 'timeslots_copy_day'),
    url(r'^roster/(?P<roster>[^/]+)/empty_day/(?P<date>\d{4}-\d{2}-\d{2})/$', timeslots_empty_day, name = 'timeslots_empty_day'),
    url(r'^roster/(?P<roster>[^/]+)/copy_day/(?P<date>\d{4}-\d{2}-\d{2})/(?P<to>[a-z]+)/$', timeslots_copy_day, name = 'timeslots_copy_day'),
    url(r'^roster/(?P<roster>[^/]+)/users/$', roster_users, name = 'roster_users'),
    url(r'^roster/(?P<roster>[^/]+)/users/submit/$', roster_users_submit, name = 'roster_users_submit'),
    url(r'^roster/(?P<roster>[^/]+)/lock/$', roster_lock, name = 'roster_lock'),
    url(r'^roster/(?P<roster>[^/]+)/invite/$', invite_workers, name = 'invite_workers'),
    url(r'^roster/(?P<roster>[^/]+)/availability/$', availability, name = 'availability'),
    url(r'^roster/(?P<roster>[^/]+)/availability/(?P<year>[0-9]+)/(?P<week>[0-9]+)/$', availability, name = 'availability'),
    url(r'^roster/(?P<roster>[^/]+)/availability/(?P<year>[0-9]+)/(?P<week>[0-9]+)/copy/$', availability_copy, name = 'availability_copy'),
    url(r'^roster/(?P<roster>[^/]+)/availability/submit/$', availability_submit, name = 'availability_submit'),
    url(r'^roster/(?P<roster>[^/]+)/stats/$', roster_stats, name = 'roster_stats'),
    url(r'^roster/(?P<roster>[^/]+)/stats/dist.png$', hour_dist_scatter, name = 'roster_stats_graph'),
    url(r'^calc/(?P<roster>[^/]+)/start/$', calculate_start, name = 'calculate_start'),
    url(r'^calc/(?P<roster>[^/]+)/restart/$', calculate_restart, name = 'calculate_restart'),
    url(r'^calc/(?P<roster>[^/]+)/status/$', calculate_status, name = 'calculate_status'),
    url(r'^calc/(?P<roster>[^/]+)/publish/$', calculate_publish, name = 'calculate_publish'),
    url(r'^timeslot/(?P<slot>[0-9]+)/$', slot_info, name = 'slot_info'),
    url(r'^timeslot/(?P<slot>[0-9]+)/delete/$', delete_timeslot, name = 'delete_timeslot'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/staff/empty/$', assignment_submit_staff_empty, name = 'assignment_submit_staff_empty'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/staff/add/$', assignment_submit_add_degeneracy, name = 'assignment_submit_add_degeneracy'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/delete_empty/$', assignment_submit_delete_empty, name = 'assignment_submit_delete_empty'),
    url(r'^timeslot/(?P<timeslot>[0-9]+)/claim/$', assignment_submit_claim, name = 'assignment_submit_claim'),
    url(r'^assignment/(?P<assignment>[0-9]+)/$', assignment_redirect),
    url(r'^assignment/(?P<assignment>[0-9]+)/submit/$', assignment_submit, name = 'assignment_submit'),
    url(r'^assignment/(?P<assignment>[0-9]+)/staff/$', assignment_submit_staff, name = 'assignment_submit_staff'),
    url(r'^assignment/(?P<assignment>[0-9]+)/submit/split/$', assignment_submit_split, name = 'assignment_submit_split'),
    url(r'^assignment/(?P<assignment>[0-9]+)/submit/gift/$', assignment_submit_gift, name = 'assignment_submit_gift'),
    url(r'^assignment/(?P<assignment>[0-9]+)/submit/transfer/$', assignment_submit_transfer, name = 'assignment_submit_transfer'),
    url(r'^assignment/(?P<assignment>[0-9]+)/trade_result/$', assignment_trade_result, name = 'assignment_trade_result'),
    url(r'^overview/$', month_overview_all, name = 'month_overview_all'),
    url(r'^overview/(?P<user>[^/]+)/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', month_overview, name = 'month_overview'),
    url(r'^overview/(?P<user>[^/]+)/$', month_overview, name = 'month_overview'),
    url(r'^ical/all.ics$', AllCalendar(), name = 'ical_all'),
    url(r'^ical/trade.ics$', TradeCalendar(), name = 'ical_trade'),
    url(r'^ical/user(?P<user>[0-9]+).ics$', OwnCalendar()), # LEGACY
    url(r'^ical2/user(?P<user>[0-9]+)_trace.ics$', AvailableCalendar()), # LEGACY
    url(r'^ical/trade/(?P<user>[^/]+).ics$', AvailableCalendar(), name = 'ical_available'),
    url(r'^ical/user/(?P<user>[^/]+).ics$', OwnCalendar(), name = 'ical_own'),
    url(r'^ical/all.html$', ical_html_all, name = 'ical_html_all'),
)


