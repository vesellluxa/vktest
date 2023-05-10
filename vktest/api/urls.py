from django.urls import include, path
from rest_framework import routers

from api.views import (FriendsViewSet, IncomingFriendRequestViewSet,
                       OutgoingFriendRequests, UserViewSet, logout,
                       obtain_token, sign_up)

router_v1 = routers.DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('friends', FriendsViewSet, basename='friends')
router_v1.register(
    'friend_requests/incoming',
    IncomingFriendRequestViewSet,
    basename='friend_requests_incoming'
)
router_v1.register(
    'friend_requests/outgoing',
    OutgoingFriendRequests,
    basename='friend_requests_outgoing'
)


urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/obtain_token/', obtain_token),
    path('v1/logout/', logout),
    path('v1/sign_up/', sign_up)
]
