
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from models import User as AquaUser

"""
class AquaAdmin(UserAdmin):
    
    fieldsets = UserAdmin.fieldsets
    fieldsets[0][1]['fields'] += ('birthday',)


admin.site.register(AquaUser, AquaAdmin)
"""
