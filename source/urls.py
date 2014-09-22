
from django.conf.urls import patterns, include, url
from django.contrib import admin
from haystack.views import SearchView
from misc.views.notification import notification
import smuggler.urls, statix.urls
import account.urls


admin.autodiscover()


urlpatterns = patterns('',
	#url(r'^$', home, name = 'home'),
	url(r'^account/', include(account.urls)),
	url(r'^admin/', include(smuggler.urls)),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^search/', SearchView(template = 'search.html'), name = 'search'),
	url(r'^$', notification, {'subject': 'Welcome', 'message': 'This is the default home page. More will probably appear soon!', 'home_button': False}, name = 'home'),
	url(r'^', include(statix.urls)),
)


