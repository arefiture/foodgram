from djoser.permissions import CurrentUserOrAdminOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CurrentUserOrAdminOrReadOnly(
    IsAuthenticatedOrReadOnly,
    CurrentUserOrAdminOrReadOnly
):
    pass
