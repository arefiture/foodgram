from django.shortcuts import get_object_or_404
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
        follower = request.user
        queryset = User.objects.filter(followings__follower=follower)
        pages = self.paginate_queryset(queryset)

        serializer = SubscriptionGetSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('POST', 'DELETE'), url_path='subscribe')
    def subscribe(self, request, id):
        data = {
            'follower': request.user,
            'followed': get_object_or_404(User, id=id)
        }

        return object_update_or_delete(
            data=data,
            error_mesage='У вас нет данного пользователя в подписчиках.',
            model=Subscription,
            request=request,
            serializer_class=SubscriptionChangedSerializer,
        )
