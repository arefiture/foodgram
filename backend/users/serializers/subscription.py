from django.conf import settings
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscription, User
from users.serializers.user import UserSerializer
from users.validators import SubscribeUniqueValidator


def get_base_recipe_serializer():
    """Отложенный импорт сериалайзера для избежания цикличного импорта."""
    from api.serializers import BaseRecipeSerializer
    return BaseRecipeSerializer


class SubscriptionGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для фолловеров. Только для чтения."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.IntegerField(
        source='recipes.count'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )
        read_only_fields = fields

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            follower=request.user, followed=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = (
            request.GET.get('recipes_limit') if request
            else settings.RECIPES_LIMIT_MAX
        )
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        serializer = get_base_recipe_serializer()
        return serializer(queryset, many=True).data


class SubscriptionChangedSerializer(serializers.ModelSerializer):
    """Сериалайзер для фолловеров. Только на запись."""
    followed = UserSerializer
    follower = UserSerializer

    class Meta:
        model = Subscription
        fields = ('followed', 'follower')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('followed', 'follower'),
                message='Нельзя повторно подписаться на пользователя'
            ),
            SubscribeUniqueValidator(
                fields=('followed', 'follower')
            )
        ]

    def validate_subscription_exists(self):
        follower = self.context.get('request').user
        followed = self.validated_data.get('followed')

        subscription = Subscription.objects.filter(
            followed=followed, follower=follower
        )
        if not subscription.exists():
            raise serializers.ValidationError(
                'У вас нет данного пользователя в подписчиках.'
            )

    def to_representation(self, instance):
        return SubscriptionGetSerializer(
            instance.follower,
            context={'request': self.context.get('request')}
        ).data