import pytest

from api.models.recipe_favorite import RecipeFavorite


@pytest.fixture
def all_favorite(third_user, all_recipes) -> list:
    favorites = [
        RecipeFavorite(author=third_user, recipe=recipe)
        for recipe in all_recipes
    ]
    RecipeFavorite.objects.bulk_create(favorites)
    return list(RecipeFavorite.objects.all())
