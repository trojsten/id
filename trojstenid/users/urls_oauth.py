from django.urls import re_path
from oauth2_provider import urls
from oauth2_provider.views import IntrospectTokenView, RevokeTokenView, TokenView

from trojstenid.users.views import TrojstenAuthorizationView

app_name = urls.app_name

base_urlpatterns = [
    re_path(r"^authorize/$", TrojstenAuthorizationView.as_view(), name="authorize"),
    re_path(r"^token/$", TokenView.as_view(), name="token"),
    re_path(r"^revoke_token/$", RevokeTokenView.as_view(), name="revoke-token"),
    re_path(r"^introspect/$", IntrospectTokenView.as_view(), name="introspect"),
]

urlpatterns = base_urlpatterns + urls.oidc_urlpatterns
