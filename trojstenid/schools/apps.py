from django.apps import AppConfig


class SchoolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "trojstenid.schools"
    label = "trojstenid_schools"
    verbose_name = "Schools"

    def ready(self):
        from . import signals  # noqa
