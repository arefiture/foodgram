from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from djoser.permissions import CurrentUserOrAdmin
from rest_framework import status, response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from core.utils import object_update_or_delete
from users.models import Subscription, User
from users.serializers import (
    AvatarSerializer,
    SubscriptionChangedSerializer,
    SubscriptionGetSerializer,
    UserSerializer
)


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'

    @action(
        ["GET", "PUT", "PATCH", "DELETE"],
        detail=False,
        # TODO: Возможно, стоит сделать отдельно perm на isCurrentUser?
        permission_classes=[CurrentUserOrAdmin]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(['PUT', 'DELETE'], detail=False, url_path='me/avatar')
    def change_avatar(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            self.request.user.avatar = None
            self.request.user.save()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        if 'avatar' not in request.data:
            return response.Response(
                {'avatar': 'Отсутствует изображение'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_data = serializer.validated_data.get('avatar')
        request.user.avatar = avatar_data
        request.user.save()

        image_url = request.build_absolute_uri(
            f'/media/users/{avatar_data.name}'
        )
        return response.Response(
            {'avatar': str(image_url)}, status=status.HTTP_200_OK
        )

    @action(['GET'], detail=False, url_path='subscriptions')
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(followings__follower=user)
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
            'followed': request.user,
            'follower': get_object_or_404(User, id=id)
        }

        return object_update_or_delete(
            data=data,
            error_mesage='У вас нет данного пользователя в подписчиках.',
            model=Subscription,
            request=request,
            serializer_class=SubscriptionChangedSerializer,
        )
