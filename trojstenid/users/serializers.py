from allauth.account.models import EmailAddress
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import serializers

from trojstenid.users.models import User


class UserSchoolRecordSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return instance.to_dict()


class EmailAddressSerializer(serializers.ModelSerializer):
    class Meta:  # type:ignore
        model = EmailAddress
        fields = ["email", "verified", "primary"]


class UserSerializer(serializers.ModelSerializer):
    current_school_record = serializers.SerializerMethodField()
    groups = serializers.SlugRelatedField(
        slug_field="name", many=True, queryset=Group.objects.get_queryset()
    )
    emails = EmailAddressSerializer(many=True, source="emailaddress_set")
    avatar = serializers.SerializerMethodField()

    class Meta:  # type:ignore
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "date_joined",
            "last_login",
            "avatar",
            "current_school_record",
            "groups",
            "emails",
        ]

    def get_current_school_record(self, obj):
        record = obj.get_current_school_record()
        return UserSchoolRecordSerializer(record).data if record else None

    def get_avatar(self, obj):
        return reverse("profile_avatar", kwargs={"user": obj.username})


class UserListSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
        ]
