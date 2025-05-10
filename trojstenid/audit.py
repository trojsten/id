import logging

from django.http import HttpRequest
from ipware import get_client_ip

from trojstenid.users.models import User

_audit_logger = logging.getLogger("trojstenid.audit")

logging.addLevelName(logging.INFO + 1, "AUDIT")


def log(request: HttpRequest, message: str, *args, **kwargs):
    user: User = request.user  # pyright: ignore
    username = user.username if user.is_authenticated else "<nobody>"
    ip, _ = get_client_ip(request)
    _audit_logger._log(
        logging.INFO + 1, f"{username} @ {ip}: {message}", args, **kwargs
    )
