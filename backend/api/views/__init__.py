from api.views.ingredient import IngredientViewSet
from api.views.recipe import RecipeRedirectView, RecipeViewSet
from api.views.tag import TagViewSet
from api.views.user import UserViewSet

__all__ = [
    'IngredientViewSet',
    'RecipeRedirectView',
    'RecipeViewSet',
    'TagViewSet',
    'UserViewSet'
]
