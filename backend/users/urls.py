from django.urls import include, path
from djoser.views import UserViewSet

from users.views import (ManageSubscribtionAPIView,
                         SubscriptionListView,
                         UserAvatarAPIView,)


app_name = 'users'

urlpatterns = [
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='user-list-create'),
    path('users/<int:id>/', UserViewSet.as_view({'get': 'retrieve'}),
         name='user-detail'),
    path('users/set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='set-password'),
    path('users/me/', UserViewSet.as_view({'get': 'me'}),
         name='user-me'),
    path('users/me/avatar/', UserAvatarAPIView.as_view(),
         name='user-me-avatar'),
    path('users/<int:id>/subscribe/', ManageSubscribtionAPIView.as_view(),
         name='user-subscribe'),
    path('users/subscriptions/', SubscriptionListView.as_view(),
         name='user-subscriptions'),
    path('auth/', include('djoser.urls.authtoken')),
]
