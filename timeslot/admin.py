
from django.contrib import admin
from timeslot.models import Roster, TimeSlot, RosterWorker


admin.site.register(Roster)
admin.site.register(TimeSlot)
admin.site.register(RosterWorker)

