from http import HTTPStatus

import pytest

from api.models.shopping_cart import ShoppingCart
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    URL_UNAUTHORIZED_ERROR,
    validate_response_scheme
)
from tests.utils.recipe import SCHEME_SHORT_RECIPE
from tests.utils.shopping_cart import (
    ALLOWED_CONTENT_TYPES,
    URL_DOWNLOAD_SHOPPING_CART,
    URL_SHOPPING_CART
)


@pytest.mark.django_db(transaction=True)
class TestShoppingCart:

    def test_add_to_shopping_cart_unauthorized(
        self, api_client, second_recipe
    ):
        url = URL_SHOPPING_CART.format(id=second_recipe.id)
        response = api_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=url)
        )

    def test_add_again_to_shopping_cart(
        self, third_user_authorized_client, all_shopping_cart, third_recipe
    ):
        url = URL_SHOPPING_CART.format(id=third_recipe.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(method='post', url=url)
        )

    def test_add_non_existing_recipe_to_shopping_cart(
        self, third_user_authorized_client
    ):
        url = URL_SHOPPING_CART.format(id=9876)
        response = third_user_authorized_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )

    def test_download_shopping_cart_unauthorized(
        self, api_client
    ):
        response = api_client.get(URL_DOWNLOAD_SHOPPING_CART)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )

    def test_add_to_shopping_cart_authorized(
        self, third_user_authorized_client, third_user, first_recipe
    ):
        count_shopping_cart = ShoppingCart.objects.count()
        url = URL_SHOPPING_CART.format(id=first_recipe.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(method='post', url=url)
        )
        new_shopping_cart_element = ShoppingCart.objects.filter(
            author=third_user, recipe=first_recipe
        )
        assert (
            new_shopping_cart_element.exists()
            and count_shopping_cart + 1 == new_shopping_cart_element.count()
        ), (
            'Убедитесь, что в БД обновились записи.'
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_SHORT_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE

    def test_download_shopping_cart_authorized(
        self, third_user_authorized_client, third_user, all_shopping_cart
    ):
        response = third_user_authorized_client.get(URL_DOWNLOAD_SHOPPING_CART)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_DOWNLOAD_SHOPPING_CART)
        )
        response_content_type = response.headers.get('Content-Type')
        # Хотелось бы проверять еще и содержимое, но от разраба к разрабу
        # форма содержимого может быть разной.
        assert response_content_type in ALLOWED_CONTENT_TYPES, (
            'Проверьте, что возвращаемый файл принадлежит к одному из '
            f'типов: {ALLOWED_CONTENT_TYPES}.'
        )
