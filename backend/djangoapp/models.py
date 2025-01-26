from django.contrib.auth.models import AbstractUser
from django.db import models


# BaseModel reste inchangé
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Remplit la date à la création
    updated_at = models.DateTimeField(auto_now=True)  # Met à jour la date à chaque modification

    class Meta:
        abstract = True  # Cette classe ne sera pas directement utilisée pour créer une table

# User hérite maintenant de AbstractUser
class User(AbstractUser):  # Remplace le modèle utilisateur par défaut de Django
    # Ajout de champs supplémentaires
    email = models.EmailField(unique=True)  # Email unique obligatoire (déjà présent dans AbstractUser mais non unique par défaut)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",  # Dossier de stockage des photos
        default="profile_pictures/default.jpg",  # Image par défaut si aucune photo n'est fournie
        blank=True  # Permet de laisser ce champ vide
    )
    pass

    def __str__(self):
        return self.username

class Block(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocking")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")  # Empêche les doublons
        verbose_name = "Block"
        verbose_name_plural = "Blocks"

    def __str__(self):
        return f"{self.blocker.username} blocked {self.blocked.username}"

# History reste inchangé
class History(BaseModel):  # Hérite également de BaseModel
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories")
    guest_name = models.CharField(max_length=50)  # Nom de l'adversaire (non utilisateur)
    user_score = models.IntegerField()  # Score de l'utilisateur
    guest_score = models.IntegerField()  # Score de l'adversaire
    played_at = models.DateTimeField(auto_now_add=True)  # Date et heure du match

    def __str__(self):
        return f"History of {self.user.username} at {self.created_at}"


