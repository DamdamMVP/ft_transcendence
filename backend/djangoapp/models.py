from django.contrib.auth.models import AbstractUser
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class User(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        default="profile_pictures/default.jpg",
        blank=True
    )
    language = models.CharField(max_length=20, default="fr")
    theme = models.CharField(max_length=20, default="dark")
    friends = models.ManyToManyField('self', symmetrical=False, blank=True)
    has_2fa = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")
        verbose_name = "Block"
        verbose_name_plural = "Blocks"

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"

class History(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories")
    guest_name = models.CharField(max_length=50)
    user_score = models.IntegerField()
    guest_score = models.IntegerField()
    played_at = models.DateTimeField(auto_now_add=True)
    game_name = models.CharField(max_length=50, default="pong")

    def __str__(self):
        return f"History of {self.user.username} at {self.created_at}"


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="status")
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
