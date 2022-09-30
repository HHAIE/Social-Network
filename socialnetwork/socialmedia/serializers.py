from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id')


class ImageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Image
        fields = ['name', 'image', 'user']


class ImageListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Image
        fields = ['name', 'image', 'thumbnail', 'user']


class StatusSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Status
        fields = ['status', 'date', 'lastDate', 'user']


class UserUserFriendSerializer(serializers.ModelSerializer):
    user1 = serializers.StringRelatedField()
    user2 = serializers.StringRelatedField()

    class Meta:
        model = UserUserFriend
        fields = ['user1', 'user2', 'date', 'chat']


class AppUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    images = ImageSerializer(many=True)
    statuses = StatusSerializer(many=True)
    friend_user1 = UserUserFriendSerializer(many=True)
    friend_user2 = UserUserFriendSerializer(many=True)

    class Meta:
        model = AppUser
        fields = ('user', 'birthDate', 'images', 'statuses',
                  'friend_user1', 'friend_user2')
