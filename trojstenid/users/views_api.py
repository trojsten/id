from django.db.models import Q
from rest_framework import generics, permissions

from trojstenid.users.models import User
from trojstenid.users.serializers import UserListSerializer, UserSerializer


class UserListView(generics.ListAPIView):
    """
    List all users.
    Search by username, email, or name using ?search=.
    """

    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user: User = self.request.user  # type:ignore
        search_query = self.request.GET.get("search", None)

        if user.is_staff:
            qs = User.objects.all()
        else:
            qs = User.objects.filter(id=user.id)

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
        except (ValueError, User.DoesNotExist):
            return qs.get(username=lookup_value)
