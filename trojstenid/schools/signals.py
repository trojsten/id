from django.db.models.signals import post_save
from django.dispatch import receiver

from trojstenid.schools.models import UserSchoolRecord
from trojstenid.users.tasks import send_user_update


@receiver(post_save, sender=UserSchoolRecord)
def user_school_record_saved(sender, instance: UserSchoolRecord, **kwargs):
    send_user_update.delay(instance.user_id)
