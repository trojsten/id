import logging
from hmac import compare_digest

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.http.response import Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions

from trojstenid.users.models import User, WifiPassword
from trojstenid.users.serializers import UserListSerializer, UserSerializer

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class RadiusCheckView(View):
    def post(self, request, *args, **kwargs):
        token = settings.RADIUS_AUTH_TOKEN
        if not token:
            return HttpResponseNotFound()

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or not compare_digest(auth[7:], token):
            return HttpResponseForbidden()

        username = request.POST.get("User-Name", "")
        password = request.POST.get("User-Password", "")
        calling_station_id = request.POST.get("Calling-Station-Id", "")

        wifi_password = WifiPassword.objects.filter(username=username).first()
        if (
            wifi_password
            and wifi_password.check_password(password)
            and wifi_password.allows_caller(calling_station_id)
        ):
            logger.info(
                "successful wifi login username=%s calling_station_id=%s nas=%s",
                username,
                calling_station_id,
                request.POST.get("NAS-Identifier", ""),
            )
            return HttpResponse("OK")
        return HttpResponseForbidden()


class UserListView(generics.ListAPIView):
    """
    List all users.
    Search by username, email, or name using ?search=.
    Optionally ?id__in= can be used (comma-separated list of user IDs) to only list specific users.
    """

    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user: User = self.request.user  # type:ignore
        search_query = self.request.GET.get("search", None)
        id_list = self.request.GET.get("id__in", None)
        if id_list:
            id_list = [int(x) for x in id_list.split(",") if x.isdigit()]

        if user.is_staff:
            qs = User.objects.all()
        else:
            qs = User.objects.filter(id=user.id)

        if id_list:
            qs = qs.filter(id__in=id_list)

        if search_query:
            qs = qs.filter(
                Q(username__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(first_name__unaccent__icontains=search_query)
                | Q(last_name__unaccent__icontains=search_query)
            )

        return qs


class UserDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single user by ID or username.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        user: User = self.request.user  # type:ignore
        lookup_value = self.kwargs.get(self.lookup_field) or self.kwargs.get("username")

        qs = User.objects.prefetch_related(
            "userschoolrecord_set", "groups", "emailaddress_set"
        )

        if not user.is_staff:
            qs = qs.filter(id=user.id)

        try:
            return qs.get(id=int(lookup_value))
        except ValueError, User.DoesNotExist:
            return qs.get(username=lookup_value)
        except User.DoesNotExist:
            raise Http404
