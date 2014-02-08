
from django.core.management import call_command
from datetime import datetime
from django.core.management.base import BaseCommand


'''
    simply export the json database
'''
class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'Store a backup in "backups" directory (should be auto-called periodically)'
    
    def handle(self, *args, **options):
        timestr = datetime.today().strftime('%Y-%m-%d_%H-%M')
        with open('backups/auto_backup_%s.json' % timestr, 'w+') as fh:
            call_command('dumpdata', stdout = fh)

