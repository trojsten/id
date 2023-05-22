from oauth2_provider import urls

app_name = urls.app_name

urlpatterns = urls.base_urlpatterns + urls.oidc_urlpatterns
