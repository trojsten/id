from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required

from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["avatar_file"]}),)


admin.site.register(User, CustomUserAdmin)
admin.site.login = login_required(admin.site.login)
