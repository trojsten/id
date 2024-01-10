from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
)
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class RemovePlaceholdersMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in self.fields:
            if "placeholder" in self.fields[name].widget.attrs:
                del self.fields[name].widget.attrs["placeholder"]


class SignupMixin(RemovePlaceholdersMixin, forms.Form):
    first_name = forms.CharField(label="Meno")
    last_name = forms.CharField(label="Priezvisko")
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    field_order = ["first_name", "last_name", "email", "username"]


class OurSignupForm(SignupMixin, SignupForm):
    pass


class OurSocialSignupForm(SignupMixin, SocialSignupForm):
    pass


class OurChangePasswordForm(RemovePlaceholdersMixin, ChangePasswordForm):
    pass


class OurResetPasswordForm(RemovePlaceholdersMixin, ResetPasswordForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


class OurResetPasswordKeyForm(RemovePlaceholdersMixin, ResetPasswordKeyForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


class OurLoginForm(RemovePlaceholdersMixin, LoginForm):
    pass


class OurSetPasswordForm(RemovePlaceholdersMixin, SetPasswordForm):
    pass


class OurAddEmailForm(RemovePlaceholdersMixin, AddEmailForm):
    pass
