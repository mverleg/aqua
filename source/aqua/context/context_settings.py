
from django.conf import settings
from django.utils.safestring import mark_safe


def context_settings(request):
	notification = ''
	try:
		with open(settings.NOTIFICATION_PATH, 'r') as fh:
			notification = mark_safe(fh.read().strip())
	except Exception:
		try:
			with open(settings.NOTIFICATION_PATH, 'w+') as fh:
				fh.write('')
		except Exception:
			print 'no notification file and not writable ({0:s})'.format(settings.NOTIFICATION_PATH)
	print notification
	return {
		'SITEWIDE_NOTIFICATION': notification,
	}


