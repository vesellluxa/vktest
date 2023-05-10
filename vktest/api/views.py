from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import FriendRequest
from api.serializers import (FriendRequestSerializer, FriendsSerializer,
                             RegistrationSerializer, TokenObtainSerializer,
                             UserSerializer)
from api.utils import (accept_friend, accept_friend_request,
                       create_friend_request, decline_friend_request,
                       delete_friend)
from users.models import User


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    @swagger_auto_schema(
        methods=['POST'],
        operation_description='Send friend request to user'
    )
    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def send_friend_request(self, request, pk):
        user = request.user
        user_to_follow = User.objects.filter(id=pk).first()
        if user == user_to_follow:
            return Response(
                'Вы не можете добавить в друзья самого себя!',
                status=status.HTTP_400_BAD_REQUEST)
        user_to_follow_username = user_to_follow.username
        if not FriendRequest.objects.filter(
                user=user,
                to=user_to_follow,
        ).exists():
            create_friend_request(user, user_to_follow)
            if not FriendRequest.objects.filter(
                    user=user_to_follow,
                    to=user,
            ).exists():
                return Response(
                    f'Вы отправили заявку в друзья'
                    f' пользователю {user_to_follow.username} !',
                    status=status.HTTP_201_CREATED
                )
            accept_friend(user, user_to_follow)
            return Response(
                f'Вы добавили в друзья'
                f' пользователя {user_to_follow.username} !',
                status=status.HTTP_201_CREATED
            )
        if user.friends.filter(
                id__in=(user_to_follow.id, )
        ).exists():
            return Response(
                f'Вы уже в друзьях'
                f' пользователя {user_to_follow_username}!',
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            f'Вы уже подписаны'
            f' на пользователя {user_to_follow_username}!',
            status=status.HTTP_400_BAD_REQUEST
        )


class FriendsViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    serializer_class = FriendsSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return User.objects.filter(
            id__in=self.request.user.friends.all()
        )

    @swagger_auto_schema(
        methods=['DELETE'],
        operation_description='Delete friend'
    )
    @action(
        methods=['DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def delete_friend(self, request, pk):
        user = request.user
        friend = User.objects.filter(
            id=pk
        ).first()
        if user.friends.filter(
                id__in=(friend.id,)
        ).exists():
            delete_friend(user, friend)
            return Response(
                f'Вы удалили из друзей'
                f' пользователя {friend.username}',
                status=status.HTTP_204_NO_CONTENT)
        return Response(
            f'Пользователь {friend.username}'
            f' не был у вас в друзьях!',
            status=status.HTTP_204_NO_CONTENT)


class IncomingFriendRequestViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   GenericViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            to=self.request.user,
            is_accepted=False,
            is_declined=False
        )

    @swagger_auto_schema(
        methods=['POST'],
        operation_description='Accept friend request'
    )
    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def accept(self, request, pk):
        friend_request = FriendRequest.objects.filter(
            id=pk
        ).first()
        accept_friend_request(
            incoming_friend_request=friend_request,
            user=request.user,
            following_user=friend_request.user
        )
        return Response(
            'Пользователь добавлен в друзья!',
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        methods=['POST'],
        operation_description='Decline friend request'
    )
    @action(
        methods=['POST'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def decline(self, request, pk):
        decline_friend_request(
            friend_request=FriendRequest.objects.filter(
                id=pk
            ).first(),
        )
        return Response(
            'Пользователь оставлен в подписчиках!',
            status=status.HTTP_204_NO_CONTENT
        )


class OutgoingFriendRequests(mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             GenericViewSet):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            user=self.request.user
        ).exclude(is_accepted=True,
                  is_declined=False)

    @swagger_auto_schema(
        methods=['DELETE'],
        operation_description='Delete friend request to user'
    )
    @action(
        methods=['DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def cancel(self, request, pk):
        friend_request = FriendRequest.objects.filter(
            id=pk
        ).first()
        following = friend_request.to
        friend_request.delete()
        return Response(
            f'Вы отписались от пользователя {following.username}!',
            status=status.HTTP_204_NO_CONTENT
        )


@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'category': openapi.Schema(type=openapi.TYPE_STRING),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    operation_description='Register'
)
@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(f'Вы успешно зарегестрировались'
                    f' под именем: {serializer.data.get("username")}',
                    status=status.HTTP_201_CREATED
                    )


@swagger_auto_schema(
    methods=['POST'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'category': openapi.Schema(type=openapi.TYPE_STRING),
            'name': openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
    operation_description='Obtain token'
)
@api_view(['POST'])
def obtain_token(request):
    serializer = TokenObtainSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.get_or_create_token()
    return Response(
        data={"auth_token": f"{token}"},
        status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    methods=['POST'],
    operation_description='Logout'
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
