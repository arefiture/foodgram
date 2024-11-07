from http import HTTPStatus

import pytest

from api.models.recipe_favorite import RecipeFavorite
from tests.utils.recipe import SCHEME_SHORT_RECIPE
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_UNAUTHORIZED_ERROR,
    validate_response_scheme
)
from tests.utils.favorite import (
    URL_FAVORITE
)


@pytest.mark.django_db(transaction=True)
class TestFavorite:

    def test_add_to_favorite_unauthorized(
        self, api_client, second_recipe
    ):
        url = URL_FAVORITE.format(id=second_recipe.id)
        response = api_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=url)
        )

    def test_add_again_to_favorite(
        self, third_user_authorized_client, third_recipe, all_favorite
    ):
        count_favorite = RecipeFavorite.objects.count()
        url = URL_FAVORITE.format(id=third_recipe.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=url)
        )
        new_count_favorite = RecipeFavorite.objects.count()
        assert count_favorite == new_count_favorite, (
            'Убедитесь, что данные в БД не изменились.'
        )

    def test_add_non_existing_recipe_to_favorite(
        self, third_user_authorized_client
    ):
        url = URL_FAVORITE.format(id=9876)
        response = third_user_authorized_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )

    def test_add_to_favorite_authorized(
        self, third_user_authorized_client, third_user, first_recipe
    ):
        count_favorite = RecipeFavorite.objects.count()
        url = URL_FAVORITE.format(id=first_recipe.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(url=url)
        )
        new_favorite = RecipeFavorite.objects.filter(
            author=third_user, recipe=first_recipe
        )
        assert (
            new_favorite.exists()
            and count_favorite + 1 == new_favorite.count()
        ), (
            'Убедитесь, что в БД появилась запись'
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_SHORT_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE
