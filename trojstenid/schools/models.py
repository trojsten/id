from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from trojstenid.schools.utils import academic_year_end, date_to_academic_year

if TYPE_CHECKING:
    from trojstenid.users.models import User


class SchoolType(models.Model):
    id: int
    identifier = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128)
    short = models.CharField(max_length=128)
    years = ArrayField(models.CharField(max_length=64), blank=True)

    class Meta:
        ordering = ["identifier"]

    def __str__(self) -> str:
        return self.name


class SchoolQuerySet(models.QuerySet):
    def search(self, query: str):
        return self.filter(
            Q(name__unaccent__icontains=query) | Q(address__unaccent__icontains=query)
        )


class School(models.Model):
    id: int
    eduid = models.IntegerField(blank=True, null=True, unique=True)
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256, blank=True)
    types = models.ManyToManyField(SchoolType)
    is_selectable = models.BooleanField(default=True)

    objects: SchoolQuerySet = SchoolQuerySet.as_manager()  # pyright:ignore

    class Meta:
        ordering = ["eduid", "name"]

    def __str__(self) -> str:
        if not self.address:
            return self.name
        return f"{self.name}, {self.address}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "eduid": self.eduid,
            "name": self.name,
            "address": self.address,
            "types": [t.identifier for t in self.types.all()],
        }


class UserSchoolRecordManager(models.Manager):
    def end_active(self, user: "User", end_date: date):
        active_records = user.userschoolrecord_set.filter(
            Q(end_date__isnull=True) | Q(end_date__gte=end_date)
        )
        active_records.update(end_date=end_date - timedelta(days=1))

    @transaction.atomic
    def end_all_expired(self, academic_year: int) -> int:
        ayear_end = academic_year_end(academic_year)
        records = (
            UserSchoolRecord.objects.filter(start_date__lte=ayear_end)
            .filter(Q(end_date__isnull=True) | Q(end_date__gt=ayear_end))
            .select_related("school_type")
        )

        changed = 0
        for record in records:
            record: UserSchoolRecord
            max_years = len(record.school_type.years) - 1
            current_year = record.get_current_year(at=ayear_end)

            if current_year >= max_years:
                end_academic_year = academic_year - (current_year - max_years)
                record.end_date = academic_year_end(end_academic_year)
                record.full_clean()
                record.save()
                changed += 1

        return changed


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

    objects: "UserSchoolRecordManager" = UserSchoolRecordManager()  # pyright: ignore

    class Meta:
        ordering = ["user_id", "start_date"]

    def __str__(self) -> str:
        return f"{self.user}, {self.school}, {self.start_date} - {self.end_date}"

    def get_start_display(self):
        ayear = date_to_academic_year(self.start_date)
        return f"{ayear}/{ayear + 1 % 100}"

    def get_current_year(self, at: date | None = None) -> int:
        if at is None:
            at = timezone.now()
        start_ayear = date_to_academic_year(self.start_date)
        current_ayear = date_to_academic_year(at)
        return current_ayear - start_ayear + self.start_year

    def get_current_year_display(self, at: date | None = None) -> str:
        years = self.school_type.years
        current_year = self.get_current_year(at)
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

    def clean(self):
        if self.end_date and self.start_date >= self.end_date:
            raise ValidationError("Dátum nástupu musí byť skôr ako dátum ukončenia.")

        q = Q(end_date__isnull=True) | Q(end_date__gte=self.start_date)
        if self.end_date:
            q &= Q(start_date__lte=self.end_date)
        collision = self.user.userschoolrecord_set.exclude(id=self.id).filter(q)

        if collision.exists():
            raise ValidationError("Tento záznam sa prekrýva s existujúcim záznamom.")

        if self.end_date:
            record_length = date_to_academic_year(
                self.end_date
            ) - date_to_academic_year(self.start_date)
            ending_year = self.start_year + record_length
            if ending_year >= len(self.school_type.years):
                raise ValidationError("Prekročená doba štúdia.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "school": self.school.to_dict(),
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "start_year": self.start_year,
            "current_year": self.get_current_year(),
            "current_year_display": self.get_current_year_display(),
            "school_type": self.school_type.identifier,
        }
