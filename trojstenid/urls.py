"""
URL configuration for trojstenid project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from trojstenid.users import views

urlpatterns = [
    path("", views.LandingPageView.as_view()),
    path("admin/", admin.site.urls),
    path("profile/", include("trojstenid.profiles.urls")),
    path("accounts/profile/", views.ProfileView.as_view(), name="account_profile"),
    path("accounts/", include("allauth.urls")),
    path("oauth/", include("trojstenid.users.urls_oauth", namespace="oauth2_provider")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
