from django import forms

from trojstenid.schools.models import School, SchoolType
from trojstenid.users.models import User


class HtmlDateInput(forms.DateInput):
    input_type = "date"


class SchoolRecordForm(forms.Form):
    start_date = forms.DateField(
        widget=HtmlDateInput, label="Dátum nástupu", help_text="Zvyčajne 1. september."
    )
    start_year = forms.ChoiceField(
        label="Počiatočný ročník",
        help_text="V ktorom ročníku si bol/a ku dátumu nástupu.",
    )
    end_date = forms.DateField(
        required=False,
        widget=HtmlDateInput,
        label="Dátum ukončenia",
        help_text="Zvyčajne 31. august, môžeš nechať prázdne.",
    )

    def get_year_choices(self) -> dict:
        if not self.school:
            return {}
        choices = {}
        for school_type in self.school.types.all():
            school_type: SchoolType
            choices[school_type.name] = {
                f"{school_type.id}:{idx}": f"{name} ({school_type.short})"
                for idx, name in enumerate(school_type.years)
            }
        return choices

    def __init__(self, school: School | None, user: User, **kwargs) -> None:
        super().__init__(**kwargs)
        self.school = school
        self.user = user
        if school:
            self.fields["start_year"].choices = self.get_year_choices()

    def clean_start_date(self):
        start_date = self.cleaned_data["start_date"]

        future_records = self.user.userschoolrecord_set.filter(
            start_date__gte=start_date
        )
        if future_records.exists():
            raise forms.ValidationError("Historické údaje nie je možné editovať.")

        return start_date
