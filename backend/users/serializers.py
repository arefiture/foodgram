from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import Recipe
from core.serializers import Base64ImageField
from users.models import Subscription, User
from users.validators import SubscribeUniqueValidator


class AvatarSerializer(serializers.Serializer):
    """Сериалайзер под аватар."""
    avatar = Base64ImageField(required=False)


class CurrentUserSerializer(DjoserUserSerializer):
    """Сериалайзер под текущего пользователя (для /me)."""
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
    """Общий сериалайзер пользователя."""
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


class RecipeShortSerializer(serializers.ModelSerializer):
    """Рецепты для отображения у фолловеров."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для фолловеров. Только для чтения."""
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed')
    recipes = serializers.SerializerMethodField(method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count')

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
        try:
            request = self.context.get('request')
            recipes_limit = request.GET.get('recipes_limit')
        except AttributeError:
            recipes_limit = 10  # TODO: вынести в настройки
        queryset = obj.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]
        return RecipeShortSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()


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

    def to_representation(self, instance):
        subscription = super().to_representation(instance)
        subscription = SubscriptionGetSerializer(
            instance.follower,
            context={'request': self.context.get('request')}
        ).data
        return subscription
