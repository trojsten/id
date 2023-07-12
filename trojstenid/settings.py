"""
Django settings for trojstenid project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

import environ

import trojstenid

env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-$$73+pr@rh27)@b^9pv$92zd6y37q&$4&n9jq!itly$@tfa@i-",
)
DEBUG = env("DEBUG", default=False)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 3600

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "trojstenid.users",
    "trojstenid.profiles",
    "widget_tweaks",
    "captcha",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.openid_connect",
    "oauth2_provider",
    "django_cleanup",
    "django_probes",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "trojstenid.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "trojstenid.context_processors.version",
            ],
        },
    },
]

WSGI_APPLICATION = "trojstenid.wsgi.application"
SITE_ID = 1

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": env.db(),
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_FORMS = {
    "add_email": "trojstenid.users.forms.allauth.OurAddEmailForm",
    "signup": "trojstenid.users.forms.allauth.OurSignupForm",
    "change_password": "trojstenid.users.forms.allauth.OurChangePasswordForm",
    "login": "trojstenid.users.forms.allauth.OurLoginForm",
    "reset_password": "trojstenid.users.forms.allauth.OurResetPasswordForm",
    "reset_password_from_key": "trojstenid.users.forms.allauth.OurResetPasswordKeyForm",
    "set_password": "trojstenid.users.forms.allauth.OurSetPasswordForm",
}

SOCIALACCOUNT_PROVIDERS = {
    "openid_connect": {
        "SERVERS": [
            {
                "id": "trojsten-login",  # 30 characters or less
                "name": "Trojsten Login",
                "server_url": "https://login.trojsten.sk",
                "APP": {
                    "client_id": env("TROJSTEN_LOGIN_CLIENT"),
                    "secret": env("TROJSTEN_LOGIN_SECRET"),
                },
                "SCOPE": ["read"],
                "VERIFIED_EMAIL": True,
            },
        ],
    }
}
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_FORMS = {
    "signup": "trojstenid.users.forms.allauth.OurSocialSignupForm",
}

RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE")

OAUTH2_PROVIDER_APPLICATION_MODEL = "users.Application"
OAUTH2_PROVIDER = {
    "OAUTH2_VALIDATOR_CLASS": "trojstenid.users.validators.OurOAuth2Validator",
    "PKCE_REQUIRED": False,
    "OIDC_ENABLED": True,
    "REQUEST_APPROVAL_PROMPT": "auto",
    "OIDC_RP_INITIATED_LOGOUT_ENABLED": True,
    "OIDC_RSA_PRIVATE_KEY": (
        "-----BEGIN PRIVATE KEY-----\n"
        f"{env('OIDC_KEY')}\n"
        "-----END PRIVATE KEY-----"
    ),
    "SCOPES": {
        "openid": "OpenID Connect",
        "profile": "Základné osobné údaje",
        "email": "E-mailová adresa",
        "groups": "Skupiny",
    },
}

vars().update(env.email(default="consolemail://"))
DEFAULT_FROM_EMAIL = env("EMAIL_FROM", default="root@localhost")

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "sk"
TIME_ZONE = "Europe/Bratislava"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_ROOT = BASE_DIR / "uploads"
MEDIA_URL = "uploads/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

if DEBUG:
    import socket  # only if you haven't already imported this

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1"]


dsn = env("SENTRY_DSN", default="")
if dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        auto_session_tracking=False,
        traces_sample_rate=0.1,
        send_default_pii=True,
        release=trojstenid.VERSION,
    )
