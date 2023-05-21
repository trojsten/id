from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import UpdateView

from trojstenid.users.forms.settings import ProfileForm


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "settings/profile.html"
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Osobné údaje uložené.")
        return redirect("account_profile")
