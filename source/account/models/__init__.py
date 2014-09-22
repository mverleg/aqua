
'''
	load models in this directory so they can be imported as
		from models import ModelName
	or
		from models import *
	which is necessary for django to recognize them
	note that django <= 1.6 also needs each model to have
		class Meta:
			app_label = 'namehere'
'''

from split_models import load_models


__all__ = load_models(__file__, locals())


