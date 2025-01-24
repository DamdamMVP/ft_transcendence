from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)  # Remplit la date à la création
    updated_at = models.DateTimeField(auto_now=True)  # Met à jour la date à chaque modification

    class Meta:
        abstract = True  # Cette classe ne sera pas directement utilisée pour créer une table

class User(BaseModel):  # Hérite de BaseModel
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=8192)  # Augmenté pour stocker le hash

    def __str__(self):
        return self.name

class History(BaseModel):  # Hérite également de BaseModel
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="histories")
    guest_name = models.CharField(max_length=50)  # Nom de l'adversaire (non utilisateur)
    user_score = models.IntegerField()  # Score de l'utilisateur
    guest_score = models.IntegerField()  # Score de l'adversaire
    played_at = models.DateTimeField(auto_now_add=True)  # Date et heure du match

    def __str__(self):
        return f"History of {self.user.name} at {self.created_at}"
