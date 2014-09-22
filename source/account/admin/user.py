
from django.contrib import admin
from account.models.user import MyUser
from muuser.admin.user import MuUserAdmin
from muuser.admin.address import ADDRESS_FIELDSET, ADDRESS_READONLY_FIELDS


class MyUserAdmin(MuUserAdmin):
	
	fieldsets = MuUserAdmin.fieldsets
	fieldsets.insert(2, ['Address', {'fields': ADDRESS_FIELDSET}])
	readonly_fields = MuUserAdmin.readonly_fields + ADDRESS_READONLY_FIELDS


admin.site.register(MyUser, MyUserAdmin)


