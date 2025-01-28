from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Generates access and refresh tokens
    TokenRefreshView,     # Renews an access token
    TokenVerifyView,      # Verifies if a token is valid
)
from . import two_factor
from . import history

urlpatterns = [
    path('', views.getData),
    path('create', views.addUser),
    path('read/<str:pk>', views.getUser),
    path('update/<str:pk>', views.updateUser),
    path('delete/<str:pk>', views.deleteUser),
    path('connect', views.connect),  # Login route
    path('update_profile_picture/<str:pk>', views.updateProfilePicture),
    path('update_password/<str:pk>', views.updatePassword),
    path('update_language/<str:pk>', views.updateLanguage),
    path('update_theme/<str:pk>', views.updateTheme),

    path('histories', history.getHistories, name='get_histories'),
    path('histories/user/<int:user_id>', history.getUserHistory, name='get_user_history'),
    path('histories/add', history.addHistory, name='add_history'),
    path('histories/update/<int:pk>', history.updateHistory, name='update_history'),
    path('histories/delete/<int:pk>', history.deleteHistory, name='delete_history'),

    path('2fa/setup', two_factor.setup_2fa, name='setup-2fa'),
    path('2fa/verify', two_factor.verify_2fa, name='verify-2fa'),
    path('2fa/disable', two_factor.disable_2fa, name='disable-2fa'),

    path('login', views.login),
    path('logout', views.logout),

    path('friends/add/<int:friend_id>', views.add_friend, name='add-friend'),
    path('friends/remove/<int:friend_id>', views.remove_friend, name='remove-friend'),
    path('friends', views.get_friends, name='get-friends'),

    path('friends/add/<str:username>', views.add_friend_by_username, name='add-friend-by-username'),
    path('friends/remove/<str:username>', views.remove_friend_by_username, name='remove-friend-by-username'),
    path('friends/list/<str:username>', views.get_friends_by_username, name='get-friends-by-username'),

    path('block', views.block_user),
    path('unblock', views.unblock_user),
    path('list_blocked', views.list_blocks),
    path('list_online', views.online_users),

    path('fortytwo/login/', views.fortytwo_login, name='fortytwo_login'),
    path('fortytwo/callback/', views.fortytwo_callback, name='fortytwo_callback'),
]
