from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from users.models import User


class CurrentUserSerializer(DjoserUserSerializer):
    """Сериалайзер под текущего пользователя (для /me)."""

    is_subscribed = serializers.BooleanField(default=False, read_only=True)

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


class UserSerializer(CurrentUserSerializer):
    """Общий сериалайзер пользователя."""

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return obj.authors.filter(user=user).exists()
