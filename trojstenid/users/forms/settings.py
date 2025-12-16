from io import BytesIO

from django import forms
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from PIL import Image
from PIL.Image import Resampling

from trojstenid.users.models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar_file"]

    def clean_avatar_file(self):
        avatar = self.cleaned_data.get("avatar_file")
        if avatar:
            w, h = get_image_dimensions(avatar)
            if w != h:
                raise ValidationError("Profilová fotka musí byť štvorec.")
            if w < 200:
                raise ValidationError("Profilová fotka musí mať aspoň 200x200px.")
            if w > 1000:
                img = Image.open(avatar).convert("RGB")
                img.thumbnail((1000, 1000), Resampling.BILINEAR)

                buffer = BytesIO()
                img.save(buffer, "jpeg")
                buffer.seek(0)

                name = avatar.name.rsplit(".", 1)[0] + ".jpeg"
                return ContentFile(buffer.read(), name=name)

        return avatar
