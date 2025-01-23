from django.urls import path
from . import views

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
]
