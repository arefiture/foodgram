import pytest

from api.models.ingredient import Ingredient
from tests.utils.ingredient import INGREDIENT_DATA


@pytest.fixture
def ingredients():
    ingredients = [Ingredient(**item) for item in INGREDIENT_DATA]
    Ingredient.objects.bulk_create(ingredients)
    return list(Ingredient.objects.all())
