
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from models import AquaUser


class AquaAdmin(UserAdmin):
    
    fieldsets = UserAdmin.fieldsets
    fieldsets[0][1]['fields'] += ('birthday',)


admin.site.register(AquaUser, AquaAdmin)


