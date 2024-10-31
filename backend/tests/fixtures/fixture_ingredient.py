import pytest

from api.models.ingredient import Ingredient
from tests.utils.ingredient import INGREDIENT_DATA


@pytest.fixture
def ingredients():
    ingredients = [Ingredient(**item) for item in INGREDIENT_DATA]
    return Ingredient.objects.bulk_create(ingredients)
