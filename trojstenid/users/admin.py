from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.decorators import login_required

from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["avatar_file"]}),)  # pyright:ignore


admin.site.register(User, CustomUserAdmin)
admin.site.site_title = "Trojsten ID"
admin.site.site_header = "Trojsten ID"


def debug_login(old_login):
    if settings.DEBUG:
        return old_login
    return login_required(old_login)


admin.site.login = debug_login(admin.site.login)
