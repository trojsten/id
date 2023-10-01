from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class BadgeGroup(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title


class Badge(models.Model):
    image = models.ImageField()
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    group = models.ForeignKey(BadgeGroup, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["group", "order", "title"]

    def __str__(self):
        return self.title


class BadgeAssignment(models.Model):
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint("badge", "user", name="badge_assignment__unique"),
        ]
