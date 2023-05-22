from django.contrib.auth.models import AbstractUser
from oauth2_provider.models import AbstractApplication


class Application(AbstractApplication):
    pass


class User(AbstractUser):
    pass
