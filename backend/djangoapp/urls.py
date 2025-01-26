from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Génère access et refresh tokens
    TokenRefreshView,     # Renouvelle un access token
    TokenVerifyView,      # Vérifie si un token est valide
)
from . import two_factor

urlpatterns = [
    path('', views.getData),
    path('create', views.addUser),
    path('read/<str:pk>', views.getUser),
    path('update/<str:pk>', views.updateUser),
    path('delete/<str:pk>', views.deleteUser),
    path('connect', views.connect),  # Route pour la connexion
    path('update_profile_picture/<str:pk>', views.updateProfilePicture),
    path('update_password/<str:pk>', views.updatePassword),
    path('histories', views.getHistories, name='get_histories'),
    path('histories/user/<int:user_id>', views.getUserHistory, name='get_user_history'),
    path('histories/add', views.addHistory, name='add_history'),
    path('histories/update/<int:pk>', views.updateHistory, name='update_history'),
    path('histories/delete/<int:pk>', views.deleteHistory, name='delete_history'),
    path('users/<str:pk>/update_password/', views.updatePassword, name='update-password'),
    path('2fa/setup', two_factor.setup_2fa, name='setup-2fa'),
    path('2fa/verify', two_factor.verify_2fa, name='verify-2fa'),
    path('2fa/disable', two_factor.disable_2fa, name='disable-2fa'),
    path('login', views.login),
    path('logout', views.logout),
]
