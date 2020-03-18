
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from timeslot.models import Roster, TimeSlot, RosterWorker


class RosterAdmin(ModelAdmin):
	list_display = ('name', 'start', 'end', 'get_state_display',)
	list_filter = ('state', 'start', 'end',)


class TimeslotAdmin(ModelAdmin):
	list_display = ('__unicode__', 'roster', 'start', 'end', 'degeneracy', 'holiday',)
	list_filter = ('roster', 'degeneracy', 'start',)


class RosterWorkerAdmin(ModelAdmin):
	list_display = ('__unicode__', 'user', 'roster', 'extra',)
	list_filter = ('user', 'roster',)


admin.site.register(Roster, RosterAdmin)
admin.site.register(TimeSlot, TimeslotAdmin)
admin.site.register(RosterWorker, RosterWorkerAdmin)
