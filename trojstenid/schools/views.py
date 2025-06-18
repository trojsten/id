from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView, ListView, TemplateView

from trojstenid.schools.forms import SchoolRecordForm
from trojstenid.schools.models import School, UserSchoolRecord
from trojstenid.users.models import User


class SchoolRecordListView(LoginRequiredMixin, ListView):
    template_name = "settings/school_list.html"

    def get_queryset(self) -> QuerySet[Any]:
        return UserSchoolRecord.objects.filter(user=self.request.user)


class SchoolRecordCreateView(LoginRequiredMixin, FormView):
    template_name = "settings/school_create.html"
    form_class = SchoolRecordForm

    @cached_property
    def school(self) -> School | None:
        school_id = self.request.GET.get("school_id")
        if not school_id:
            return None
        if not school_id.isnumeric():
            return None
        return School.objects.filter(id=school_id).first()

    def get_form_kwargs(self) -> dict[str, Any]:
        kw = super().get_form_kwargs()
        kw["school"] = self.school
        kw["user"] = self.request.user
        return kw

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["school"] = self.school
        return ctx

    @transaction.atomic
    def form_valid(self, form: SchoolRecordForm):  # pyright: ignore
        assert isinstance(self.request.user, User)

        type_id, year = form.cleaned_data["start_year"].split(":")
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]

        UserSchoolRecord.objects.end_active(self.request.user, start_date)
        record = UserSchoolRecord(
            user=self.request.user,
            school=self.school,
            start_date=start_date,
            end_date=end_date,
            school_type_id=type_id,
            start_year=year,
        )
        try:
            record.full_clean()
        except ValidationError as e:
            form.add_error(None, e)
            transaction.set_rollback(True)
            return self.form_invalid(form)
        record.save()

        return HttpResponseRedirect(reverse("account_school"))


class SchoolSearchView(LoginRequiredMixin, TemplateView):
    template_name = "settings/school_search.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "")
        ctx["schools"] = School.objects.search(query)[:10]
        return ctx
