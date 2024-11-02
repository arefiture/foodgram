from http import HTTPStatus

import pytest

from api.models.ingredient import Ingredient
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    URL_METHOD_NOT_ALLOWED,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    validate_response_scheme,
)
from tests.utils.ingredient import (
    INGREDIENT_SEARCH_DATA,
    SCHEME_INGREDIENT,
    URL_GET_INGREDIENT,
    URL_INGREDIENTS,
    DENY_CHANGE_METHOD
)


@pytest.mark.django_db(transaction=True)
class TestIngredient:

    @pytest.mark.parametrize(
        'method, method_info', DENY_CHANGE_METHOD.items()
    )
    def test_bad_request_methods(
        self, first_user_authorized_client, ingredients, method, method_info
    ):
        url = method_info['url']
        response = getattr(first_user_authorized_client, method)(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            URL_METHOD_NOT_ALLOWED.format(method=method.upper(), url=url)
        )

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_ingredients(
        self, client, ingredients
    ):
        response = client.get(URL_INGREDIENTS)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_INGREDIENTS)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_INGREDIENTS)
        )
        response_json = response.json()
        assert isinstance(response_json, list) and validate_response_scheme(
            response_json[0], SCHEME_INGREDIENT
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize('name', INGREDIENT_SEARCH_DATA)
    def test_get_ingredients_with_name_filter(
        self, first_user_authorized_client, ingredients, name
    ):
        url = URL_INGREDIENTS + '?name=' + name
        response = first_user_authorized_client.get(url)
        count_DB = Ingredient.objects.filter(
            name__startswith=name
        ).distinct().count()
        response_json = response.json()
        response_count = len(response_json)
        # Проверка существования и доступности была выше
        assert count_DB == response_count, (
            'Убедитесь, что фильтрация работает корректно. Ожидалось '
            f'{count_DB} элементов, пришло {response_count}.'
        )

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_ingredient_detail(self, client, ingredients):
        id_tag = ingredients[0].id
        url = URL_GET_INGREDIENT.format(id=id_tag)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=url)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_INGREDIENT
        ), RESPONSE_PAGINATED_STRUCTURE

    def test_non_existing_ingredient(self, client, ingredients):
        id_tag = max(ingredient.id for ingredient in ingredients)
        url = URL_GET_INGREDIENT.format(id=id_tag + 1)
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
