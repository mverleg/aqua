
from django.conf import settings
from django.utils.safestring import mark_safe


def context_settings(request):
	return {
		'SITEWIDE_NOTIFICATION': mark_safe(settings.SITEWIDE_NOTIFICATION),
	}


