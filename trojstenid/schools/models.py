from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from trojstenid.schools.utils import date_to_academic_year


class SchoolType(models.Model):
    id: int
    identifier = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    short = models.CharField(max_length=128)
    years = ArrayField(models.CharField(max_length=64), blank=True)

    def __str__(self) -> str:
        return self.name


class School(models.Model):
    id: int
    eduid = models.IntegerField(blank=True, null=True, unique=True)
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256, blank=True)
    types = models.ManyToManyField(SchoolType)
    is_selectable = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name}, {self.address}"


class UserSchoolRecord(models.Model):
    id: int
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_id: int
    school = models.ForeignKey(School, on_delete=models.RESTRICT)
    school_id: int
    school_type = models.ForeignKey(SchoolType, on_delete=models.RESTRICT)
    school_type_id: int
    start_date = models.DateField()
    start_year = models.PositiveIntegerField(default=0)
    end_date = models.DateField(blank=True, null=True)

    def get_start_display(self):
        ayear = date_to_academic_year(self.start_date)
        return f"{ayear}/{ayear + 1 % 100}"

    def get_current_year(self) -> int:
        start_ayear = date_to_academic_year(self.start_date)
        current_ayear = date_to_academic_year(timezone.now())
        return current_ayear - start_ayear + self.start_year

    def get_current_year_display(self) -> str:
        years = self.school_type.years
        current_year = self.get_current_year()
        if current_year >= len(years):
            return "?"
        return years[current_year]

    def is_active(self):
        now = timezone.now().date()
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
