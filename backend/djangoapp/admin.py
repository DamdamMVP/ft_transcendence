from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, History

# Register your models here.

# Enregistrer le modèle User avec UserAdmin
admin.site.register(User, UserAdmin)

# Enregistrer le modèle History
admin.site.register(History)
