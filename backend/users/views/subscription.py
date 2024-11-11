from django.shortcuts import get_object_or_404
from djoser.permissions import CurrentUserOrAdmin
from rest_framework.decorators import action

from core.utils import object_update_or_delete
from users.models import Subscription, User
from users.serializers import (
    SubscriptionChangedSerializer,
    SubscriptionGetSerializer
)


class SubscriptionMixin:
    @action(['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(authors__user=user)
        pages = self.paginate_queryset(queryset)

        serializer = SubscriptionGetSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        permission_classes=[CurrentUserOrAdmin]
    )
    def subscribe(self, request, id):
        data = {
            'user': request.user,
            'author_recipe': get_object_or_404(User, id=id)
        }

        return object_update_or_delete(
            data=data,
            error_mesage='У вас нет данного пользователя в подписчиках.',
            model=Subscription,
            request=request,
            serializer_class=SubscriptionChangedSerializer,
        )
