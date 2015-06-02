
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from distribute.models import Availability, Assignment


class AvailabilityAdmin(ModelAdmin):
	list_display = ('__unicode__', 'user', 'timeslot',)
	list_filter = ('user', 'timeslot__roster',)


class AssignmentAdmin(ModelAdmin):
	list_display = ('__unicode__', 'user', 'timeslot', 'fortrade', 'note',)
	list_filter = ('user', 'timeslot__roster', 'fortrade',)


admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(Assignment, AssignmentAdmin)


