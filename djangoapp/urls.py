from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Génère access et refresh tokens
    TokenRefreshView,     # Renouvelle un access token
    TokenVerifyView,      # Vérifie si un token est valide
)

urlpatterns = [
    path('', views.getData),
    path('create', views.addUser),
    path('read/<str:pk>', views.getUser),
    path('update/<str:pk>', views.updateUser),
    path('delete/<str:pk>', views.deleteUser),
    path('connect', views.connect),  # Route pour la connexion
    path('histories', views.getHistories, name='get_histories'),
    path('histories/user/<int:user_id>', views.getUserHistory, name='get_user_history'),
    path('histories/add', views.addHistory, name='add_history'),
    path('histories/update/<int:pk>', views.updateHistory, name='update_history'),
    path('histories/delete/<int:pk>', views.deleteHistory, name='delete_history'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify', TokenVerifyView.as_view(), name='token_verify'),
]
