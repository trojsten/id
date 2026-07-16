from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView, UpdateView
from oauth2_provider.views import AuthorizationView

from trojstenid.users.forms.settings import ProfileForm
from trojstenid.users.groups import VEDUCI_GROUP, WIFI_GROUP
from trojstenid.users.models import Application, User, WifiPassword
from trojstenid.users.tasks import sync_groups


class VeduciRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows access only to veduci."""

    def test_func(self):
        return self.request.user.groups.filter(name=VEDUCI_GROUP).exists()


class WifiRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Allows access only to wifi users."""

    def test_func(self):
        return self.request.user.groups.filter(name=WIFI_GROUP).exists()


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


class WifiPasswordView(WifiRequiredMixin, TemplateView):
    template_name = "settings/wifi.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wifi_password"] = WifiPassword.objects.filter(
            user=self.request.user
        ).first()
        return context

    def post(self, request, *args, **kwargs):
        wifi_password, _ = WifiPassword.objects.get_or_create(
            user=request.user,
            defaults={"username": request.user.username, "password": ""},
        )
        raw_password = wifi_password.set_password()
        wifi_password.save()
        messages.success(request, "Wi-Fi heslo bolo vygenerované.")

        context = self.get_context_data(**kwargs)
        context["wifi_password"] = wifi_password
        context["generated_password"] = raw_password
        return self.render_to_response(context)


class GroupListView(VeduciRequiredMixin, TemplateView):
    template_name = "groups/group_list.html"

    def get_context_data(self, **kwargs):
        assert isinstance(self.request.user, User)
        context = super().get_context_data(**kwargs)
        context["groups"] = self.request.user.groups.order_by("name")
        return context


class GroupSyncView(VeduciRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        sync_groups.delay()
        messages.success(request, "Synchronizácia skupín bola spustená na pozadí.")
        return redirect("group_list")
