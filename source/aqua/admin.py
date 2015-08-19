
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from models import AquaUser


class AquaAdmin(UserAdmin):

	list_display = ('username', 'first_name', 'last_name', 'is_active', 'is_staff',)
	fieldsets = UserAdmin.fieldsets
	fieldsets[0][1]['fields'] += ('birthday',)

	def get_queryset(self, request):
		qs = self.model.allobjects.get_queryset()
		ordering = self.ordering or () # otherwise we might try to *None, which is bad ;)
		if ordering:
			qs = qs.order_by(*ordering)
		return qs


admin.site.register(AquaUser, AquaAdmin)
admin.site.unregister(Group)


