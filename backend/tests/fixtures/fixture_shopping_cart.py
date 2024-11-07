import pytest

from api.models.shopping_cart import ShoppingCart


@pytest.fixture
def all_shopping_cart(third_user, all_recipes) -> list:
    shopping_cart = [
        ShoppingCart(author=third_user, recipe=recipe)
        for recipe in all_recipes
    ]
    ShoppingCart.objects.bulk_create(shopping_cart)
    return list(ShoppingCart.objects.all())
