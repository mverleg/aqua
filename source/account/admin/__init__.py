
'''
	load all the modules in the subdirectories,
	then do nothing with them, just so that they
	will register themselves with admin
'''

from split_models import check_files


__all__ = check_files(__file__)


