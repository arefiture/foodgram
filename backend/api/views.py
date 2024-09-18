from djoser import views as djoser_views
from djoser.conf import settings
from djoser.permissions import CurrentUserOrAdmin
from rest_framework import status, response
from rest_framework.decorators import action, permission_classes
from .serializers import AvatarSerializer, UserSerializer

from backend.settings import DJOSER
from users.models import User


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [CurrentUserOrAdmin]

    @action(
        ["get", "put", "patch", "delete"],
        detail=False,
        permission_classes=[CurrentUserOrAdmin]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    # def get_permissions(self):
    #     if self.action == "me":
    #         self.permission_classes = [CurrentUserOrAdmin]
    #     else:
    #         self.get_permissions()

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
