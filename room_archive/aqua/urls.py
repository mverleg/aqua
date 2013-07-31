
from django.conf.urls import patterns, url, include
#from django.contrib.auth.views import login, logout
from extra.views import mainpage
from booking import urls as booking_urls
from working import urls as working_urls
from django.contrib import admin
from general.views import login, logout
admin.autodiscover()


urlpatterns = patterns('',
    #url(r'^$', mainpage, name = 'mainpage'),
    #url(r'^login/$', login, {'template_name': 'login.html'}, name = 'login'),
    #url(r'^logout/$', logout, {'template_name': 'logout.html'}, name = 'logout'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^book/', include(booking_urls)),
    #url(r'^work/', include(working_urls)),
	url(r'^login/$', login, name='login'),
	url(r'^logout/$', logout, name='logout'),
	url(r'', include(working_urls)),
)

