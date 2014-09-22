
import settings


'''
	put some settings into javascript
'''
def javascript_settings(request):
	return {'EXTRA_JS_SETTINGS': {
		#'SITE_URL': settings.SITE_URL,
	}}


