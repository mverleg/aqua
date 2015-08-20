
from django.conf import settings
from django.utils.safestring import mark_safe


def context_settings(request):
	notification = ''
	try:
		with open(settings.NOTIFICATION_PATH) as fh:
			notification = mark_safe(fh.read())
	except Exception:
		pass
	return {
		'SITEWIDE_NOTIFICATION': notification,
	}


