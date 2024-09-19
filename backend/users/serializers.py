from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from core.serializers import Base64ImageField
from users.models import Subscription, User


class AvatarSerializer(serializers.Serializer):
    avatar = Base64ImageField(required=False)


class CurrentUserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return False


class UserSerializer(CurrentUserSerializer):
    def get_is_subscribed(self, obj):
        request = self.context['request']
        try:
            Subscription.objects.get(
                follower_id=request.user.id,
                followed_id=obj.id
            )
            return True
        except Subscription.DoesNotExist:
            return False
