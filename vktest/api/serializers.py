from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from api.models import FriendRequest
from users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        validated_data['password'] = self.initial_data.get(
            'password')
        user = self.Meta.model.objects.create_user(**validated_data)
        return user


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class UserSerializer(SimpleUserSerializer):
    friends_count = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()
    friends = SimpleUserSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'friends_count',
            'subscribers',
            'id',
            'friends'
        )

    def get_friends_count(self, instance):
        return instance.friends.count()

    def get_subscribers(self, instance):
        return FriendRequest.objects.filter(
            to=instance
        ).count()

    def create(self, validated_data):
        print(validated_data)
        user = self.Meta.model.objects.create_user(**validated_data)
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    to = SimpleUserSerializer()

    class Meta:
        model = FriendRequest
        fields = (
            'to',
            'id'
        )


class FriendsSerializer(UserSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'username',
            'status',
            'friends_count',
            'subscribers',
            'id',
            'friends'
        )

    def get_status(self, instance):
        user = self.context['request'].user
        is_friend = user.friends.filter(
            id__in=(instance.id,)
        ).exists()
        if is_friend:
            return 'У вас в друзьях'
        if FriendRequest.objects.filter(
                user=user,
                to=instance,
                is_declined=True
        ).exists():
            return 'Вы подписаны'
        if FriendRequest.objects.filter(
                user=instance,
                to=user
        ).exists():
            return 'Подписан на вас'
        return 'Не в друзьях'


class TokenObtainSerializer(serializers.Serializer):
    password = serializers.CharField()
    username = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            raise ValidationError('Username is invalid')
        raw_password = data.get('password')
        if not user.check_password(raw_password):
            raise ValidationError('Password is invalid')
        return data

    def get_or_create_token(self):
        user = User.objects.get(username=self.data.get('username'))
        token = Token.objects.get_or_create(user=user)[0]
        return token
