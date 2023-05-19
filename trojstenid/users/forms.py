from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms


class RemovePlaceholdersMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in self.fields:
            if "placeholder" in self.fields[name].widget.attrs:
                del self.fields[name].widget.attrs["placeholder"]


class SignupMixin(RemovePlaceholdersMixin, forms.Form):
    first_name = forms.CharField(label="Meno")
    last_name = forms.CharField(label="Priezvisko")

    field_order = ["first_name", "last_name", "email", "username"]


class OurSignupForm(SignupMixin, SignupForm):
    pass


class OurSocialSignupForm(SignupMixin, SocialSignupForm):
    pass
