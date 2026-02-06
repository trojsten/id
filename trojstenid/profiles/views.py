import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, TemplateView
from PIL import ImageColor

from trojstenid.badges.models import Badge
from trojstenid.users.models import User


class AvatarView(TemplateView):
    template_name = "profile/avatar.svg"
    content_type = "image/svg+xml"

    def get(self, request, *args, **kwargs):
        self._user: User = get_object_or_404(
            User, username=kwargs["user"], is_active=True
        )
        if self._user.avatar_file:
            return HttpResponseRedirect(self._user.avatar_file.url)

        return super().get(request, *args, **kwargs)

    def get_text_color(self, background: str) -> str:
        r, g, b, *_ = ImageColor.getrgb(background)
        return "#000000" if (r * 0.299 + g * 0.587 + b * 0.114) > 150 else "#ffffff"

    def get_context_data(self, **kwargs):
        initials = "".join([x[0] for x in self._user.get_full_name().split()]).upper()
        ctx = super().get_context_data(**kwargs)
        hue = random.Random(self._user.id).randint(0, 360)  # noqa: S311
        background = ImageColor.getrgb(f"hsl({hue}, 100%, 60%)")
        background = "#" + "".join([f"{x:02x}" for x in background])

        ctx["background"] = background
        ctx["color"] = self.get_text_color(background)
        ctx["text"] = initials
        return ctx


class ProfileView(LoginRequiredMixin, DetailView):
    template_name = "profile/profile.html"

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs["user"], is_active=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = ctx["object"]
        ctx["groups"] = user.groups.values_list("name", flat=True)
        ctx["badges"] = Badge.objects.filter(badgeassignment__user=user)
        return ctx
