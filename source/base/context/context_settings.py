
import settings


'''
	put some settings into the default context
	note that misc has a similar processor; your setting may already be added
'''
def context_settings(request):
	return {
		#'EXAMPLE': settings.EXAMPLE,
	}


