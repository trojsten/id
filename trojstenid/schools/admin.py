from django.contrib import admin

from trojstenid.schools.models import School, SchoolType, UserSchoolRecord


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "address", "eduid"]
    search_fields = ["name", "address", "eduid"]


@admin.register(SchoolType)
class SchoolTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(UserSchoolRecord)
class UserSchoolRecordAdmin(admin.ModelAdmin):
    autocomplete_fields = ["school", "user"]
    list_display = ["user", "school", "start_year"]
    search_fields = ["user__username"]


class UserSchoolRecordInline(admin.TabularInline):
    model = UserSchoolRecord
    autocomplete_fields = ["school", "user"]
