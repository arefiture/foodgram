from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework.permissions import (
    BasePermission,
    IsAuthenticatedOrReadOnly,
    SAFE_METHODS
)


class CurrentUserOrAdminOrReadOnly(
    IsAuthenticatedOrReadOnly,
    CurrentUserOrAdminOrReadOnly
):
    pass


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
