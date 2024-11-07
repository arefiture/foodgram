from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture

from api.models.recipe import Recipe
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    SCHEMA_PAGINATE,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    validate_response_scheme
)
from tests.utils.recipe import SCHEME_SHORT_RECIPE
from tests.utils.subscription import (
    SCHEME_SUBSCRIPTION,
    URL_CREATE_SUBSCRIBE,
    URL_GET_SUBSCRIPTIONS
)
from users.models.subscription import Subscription


@pytest.mark.django_db(transaction=True)
class TestSubscription:

    def test_add_subscribe_unauthorized(
        self, api_client, second_user
    ):
        count_subscriptions = Subscription.objects.all().count()
        url = URL_CREATE_SUBSCRIBE.format(id=second_user.id)
        response = api_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(method='post', url=url)
        )
        new_count_subscriptions = Subscription.objects.all().count()
        assert count_subscriptions == new_count_subscriptions, (
            'Убедитесь, что в БД не обновились записи.'
        )

    def test_add_duplicated_subscription(
        self, third_user_authorized_client, third_user_subscribed_to_second,
        second_user
    ):
        count_subscriptions = Subscription.objects.all().count()
        url = URL_CREATE_SUBSCRIBE.format(id=second_user.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(method='post', url=url)
        )
        new_count_subscriptions = Subscription.objects.all().count()
        assert count_subscriptions == new_count_subscriptions, (
            'Убедитесь, что в БД не обновились записи.'
        )

    def test_add_self_subscription(
        self, third_user_authorized_client, third_user
    ):
        count_subscriptions = Subscription.objects.all().count()
        url = URL_CREATE_SUBSCRIBE.format(id=third_user.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(method='post', url=url)
        )
        new_count_subscriptions = Subscription.objects.all().count()
        assert count_subscriptions == new_count_subscriptions, (
            'Убедитесь, что в БД не обновились записи.'
        )

    def test_add_subscription_to_non_existing_author(
        self, third_user_authorized_client
    ):
        count_subscriptions = Subscription.objects.all().count()
        url = URL_CREATE_SUBSCRIBE.format(id=9786)
        response = third_user_authorized_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        new_count_subscriptions = Subscription.objects.all().count()
        assert count_subscriptions == new_count_subscriptions, (
            'Убедитесь, что в БД не обновились записи.'
        )

    def test_add_subscribe_authorized(
        self, third_user_authorized_client, first_user, third_user, all_recipes
    ):
        count_subscriptions = Subscription.objects.all().count()
        url = URL_CREATE_SUBSCRIBE.format(id=first_user.id)
        response = third_user_authorized_client.post(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(method='post', url=url)
        )

        new_subscription = Subscription.objects.filter(
            author_recipe=first_user,
            user=third_user
        )
        assert (
            new_subscription.exists()
            and count_subscriptions + 1 == new_subscription.count()
        ), (
            'Убедитесь, что подписка на пользователя успешно создана.'
        )

        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_SUBSCRIPTION
        ), RESPONSE_PAGINATED_STRUCTURE
        response_recipes = response_json.get('recipes', [])
        response_recipes_count = response_json.get('recipes_count', 0)
        assert len(response_recipes) == response_recipes_count, (
            'Убедитесь, что количество `recipes` равно `recipes_count`.'
        )
        if response_recipes_count:
            recipe = response_recipes[0]
            assert validate_response_scheme(
                recipe, SCHEME_SHORT_RECIPE
            ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize('recipes_limit', [1, 5, 10])
    def test_add_subscribe_authorized_with_recipes_limit_param(
        self, third_user_authorized_client, second_user,
        all_recipes, recipes_limit
    ):
        url = URL_CREATE_SUBSCRIBE.format(id=second_user.id) + (
            '?recipes_limit=' + str(recipes_limit)
        )
        response = third_user_authorized_client.post(url)
        response_json = response.json()
        response_recipes = response_json.get('recipes', [])
        count_recipe_DB = (
            Recipe.objects.filter(author=second_user).distinct().count()
        )
        expected_count = (
            recipes_limit if recipes_limit < count_recipe_DB
            else count_recipe_DB
        )
        assert len(response_recipes) == expected_count, (
            'Должна быть возможность изменить количество выводимых рецептов в '
            'данных пользователя через параметр `recipes_limit`'
        )

    @pytest.mark.parametrize(
        'author',
        [lazy_fixture('first_user'), lazy_fixture('second_user')]
    )
    def test_get_subscription_list(
        self, third_user_authorized_client, third_user_subscriptions,
        third_user, author
    ):
        response = third_user_authorized_client.get(URL_GET_SUBSCRIPTIONS)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_GET_SUBSCRIPTIONS)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(method='post', url=URL_GET_SUBSCRIPTIONS)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_PAGINATE
        ), RESPONSE_PAGINATED_STRUCTURE
        response_results = response_json.get('results', [])
        count_subscribe_DB = (
            Subscription.objects.filter(user=third_user).distinct()
        )
        assert (
            count_subscribe_DB.exists()
            and len(response_results) == count_subscribe_DB.count()
        ), (
            'Убедитесь, что отобразились все записи по пользователю.'
        )
        subscription = response_results[0]
        assert validate_response_scheme(
            subscription, SCHEME_SUBSCRIPTION
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize('limit', [1, 5])
    def test_get_subscription_list_with_limit_param(
        self, third_user_authorized_client, third_user_subscriptions,
        limit
    ):
        url = URL_GET_SUBSCRIPTIONS + '?limit=' + str(limit)
        response = third_user_authorized_client.get(url)
        response_json = response.json()
        response_count = response_json.get('count', 0)
        response_results = response_json.get('results', [])
        expected_count = limit if limit < response_count else response_count
        assert len(response_results) == expected_count, (
            'Убедитесь что работает пагинация.'
        )

    @pytest.mark.parametrize('recipes_limit', [1, 5, 10])
    def test_get_subscription_list_with_recipes_limit_param(
        self, third_user_authorized_client, third_user_subscribed_to_second,
        all_recipes, recipes_limit
    ):
        url = URL_GET_SUBSCRIPTIONS + '?recipes_limit=' + str(recipes_limit)
        response = third_user_authorized_client.get(url)
        response_json = response.json()
        subscription = response_json['results'][0]
        recipes = subscription['recipes']
        recipes_count = subscription['recipes_count']
        expected_count = (
            recipes_limit if recipes_limit < recipes_count else recipes_count
        )
        assert len(recipes) == expected_count, (
            'Должна быть возможность изменить количество выводимых рецептов в '
            'данных пользователя через параметр `recipes_limit`'
        )
