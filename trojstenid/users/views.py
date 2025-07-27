from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, UpdateView
from oauth2_provider.views import AuthorizationView

from trojstenid.users.forms.settings import ProfileForm
from trojstenid.users.models import Application


class TrojstenAuthorizationView(AuthorizationView):
    def dispatch(self, request, *args, **kwargs):
        application = get_object_or_404(
            Application, client_id=request.GET.get("client_id")
        )

        if application.group:
            if not request.user.is_authenticated:
                return self.handle_no_permission()

            if not request.user.groups.contains(application.group):
                return render(
                    request,
                    "oauth2_provider/authorize.html",
                    {
                        "error": {
                            "error": "Chýbajúce oprávnenia.",
                            "description": "Nemáš práva na prístup do tejto aplikácie.",
                        }
                    },
                )

        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "settings/profile.html"
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Osobné údaje uložené.")
        return redirect("account_profile")


class LandingPageView(TemplateView):
    template_name = "landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("account_profile")
        return super().dispatch(request, *args, **kwargs)
