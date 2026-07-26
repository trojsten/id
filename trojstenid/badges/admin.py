from django.contrib import admin

from trojstenid.badges.models import Badge, BadgeAssignment, BadgeGroup


class BadgeAssignmentInline(admin.TabularInline):
    model = BadgeAssignment
    autocomplete_fields = ["user"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("badge", "user")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_filter = ["group", "title"]
    inlines = [BadgeAssignmentInline]


@admin.register(BadgeGroup)
class BadgeGroupAdmin(admin.ModelAdmin):
    list_filter = ["title"]
