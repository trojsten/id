from django.contrib import admin

from trojstenid.badges.models import Badge, BadgeAssignment, BadgeGroup


class BadgeAssignmentInline(admin.TabularInline):
    model = BadgeAssignment


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_filter = ["group", "title"]
    inlines = [BadgeAssignmentInline]


@admin.register(BadgeGroup)
class BadgeGroupAdmin(admin.ModelAdmin):
    list_filter = ["title"]
