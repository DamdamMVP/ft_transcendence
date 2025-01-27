from django.contrib.auth.models import AbstractUser
from django.db import models


# BaseModel remains unchanged
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Fills the date at creation
    updated_at = models.DateTimeField(auto_now=True)  # Updates the date on each modification

    class Meta:
        abstract = True  # This class won't be directly used to create a table

# User now inherits from AbstractUser
class User(AbstractUser):  # Replaces Django's default user model
    # Additional fields
    email = models.EmailField(unique=True)  # Required unique email (already present in AbstractUser but not unique by default)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",  # Storage folder for photos
        default="profile_pictures/default.jpg",  # Default image if no photo is provided
        blank=True  # Allows this field to be empty
    )
    language = models.CharField(max_length=20, default="fr")
    theme = models.CharField(max_length=20, default="dark")
    friends = models.ManyToManyField('self', symmetrical=False, blank=True)

    def __str__(self):
        return self.username

class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")  # Prevents duplicates
        verbose_name = "Block"
        verbose_name_plural = "Blocks"

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"

# History remains unchanged
class History(BaseModel):  # Also inherits from BaseModel
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories")
    guest_name = models.CharField(max_length=50)  # Name of the opponent (non-user)
    user_score = models.IntegerField()  # User's score
    guest_score = models.IntegerField()  # Opponent's score
    played_at = models.DateTimeField(auto_now_add=True)  # Date and time of the match
    game_name = models.CharField(max_length=50, default="pong")

    def __str__(self):
        return f"History of {self.user.username} at {self.created_at}"


class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="status")
    is_online = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"
