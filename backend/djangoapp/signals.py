from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from .models import UserStatus

@receiver(user_logged_out)
def update_user_status_on_logout(sender, user, request, **kwargs):
    if user:
        status, _ = UserStatus.objects.get_or_create(user=user)
        status.is_online = False
        status.save()
