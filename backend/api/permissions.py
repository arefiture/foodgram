from django.db.models import Model
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

CHANGE_METHODS = ('PUT', 'PATCH', 'DELETE')


class ReadOnly(BasePermission):
    """Проверка на разрешение только редактирования."""

    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        return request.method in SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Проверка на доступность только автору или только на чтение.
    """

    # Без этого работать не будет!
    # Т.к. запретили использовать наследование от IsAuthenticated
    # то вот больше кода:
    def has_permission(self, request: Request, view: GenericViewSet) -> bool:
        return (
            request.user and request.user.is_authenticated
            or request.method in SAFE_METHODS
        )

    def has_object_permission(
        self, request: Request, view: GenericViewSet, obj: Model
    ) -> bool:
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user
