
from django_cal.views import Events  # @UnresolvedImport
from distribute.models import Assignment
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models.query_utils import Q
from pytz import timezone, UTC
from datetime import timedelta


def dst_offset(dt, tz = timezone('Europe/Berlin')):
	return tz.normalize(dt.replace(tzinfo = tz)).replace(tzinfo = None) - dt.replace(tzinfo = tz).replace(tzinfo = None)

def localize(dt):
	return (dt - timedelta(hours = 1) - dst_offset(dt)).replace(tzinfo = timezone('UTC'))

class AllCalendar(Events):
	
	def items(self):
		return Assignment.objects.all()
	
	def filename(self):
		return 'shifts_all.ics'
	
	def cal_name(self):
		return 'Zaalwacht (iedereen)'
	
	def cal_desc(self):
		return None
	
	def item_summary(self, item):
		name = unicode(item.user)
		if item.fortrade == 1:
			name = '%s (te ruil)' % name
		elif item.fortrade == 2:
			name = '%s (weg te geven)' % name
		return name
	
	def item_comment(self, item):
		if item.note:
			return '%s "%s"' % (item.timeslot.roster.name, item.note)
		else:
			return item.timeslot.roster.name
	
	def item_start(self, item):
		#tz = pytz.timezone('Europe/Amsterdam')
		#t = tz.localize(item.timeslot.start)
		#print 'TZ: %s' % t.tzname()
		return localize(item.timeslot.start)
	
	def item_end(self, item):
		return localize(item.timeslot.end)
	

class TradeCalendar(AllCalendar):
	
	def items(self):
		return Assignment.objects.filter(fortrade__in = [1, 2])
	
	def cal_name(self):
		return 'Ruilshifts'
	
	def filename(self):
		return 'shifts_trade.ics'
	
	def item_summary(self, item):
		if item.fortrade == 1:
			return 'te ruil (%s)' % unicode(item.user)
		elif item.fortrade == 2:
			return 'weg te geven (%s)' % unicode(item.user)
		return '?'
	

class OwnCalendar(AllCalendar):
	
	def get_object(self, request, user):
		try:
			user = int(user)
		except ValueError:
			return get_object_or_404(User, username = user)
		return get_object_or_404(User, pk = int(user))
	
	def items(self, obj):
		return Assignment.objects.filter(user = obj)
	
	def cal_name(self, obj):
		return 'Zaalwacht (%s)' % obj.username
	
	def filename(self, obj):
		return 'shifts_%s.ics' % ''.join(ch for ch in obj.username if ch.isalnum())
	
	def item_summary(self, item):
		name = 'Zaalwacht'
		if item.fortrade == 1:
			name = '%s (te ruil)' % name
		elif item.fortrade == 2:
			name = '%s (weg te geven)' % name
		return name
	

class AvailableCalendar(OwnCalendar):
	
	def items(self, obj):
		return Assignment.objects.filter(Q(user = obj) | Q(fortrade__in = [1, 2]))
	
	def item_summary(self, item):
		name = unicode(item.user)
		if item.fortrade == 1:
			name = '%s (te ruil)' % name
		elif item.fortrade == 2:
			name = '%s (weg te geven)' % name
		else:
			name = 'zaalwacht %s' % name
		return name
	
	def cal_name(self, obj):
		return 'Zaalwacht (%s) en ruilshifts' % obj.username
	
	def filename(self, obj):
		return 'shifts_%s_trade.ics' % ''.join(ch for ch in obj.username if ch.isalnum())
	


