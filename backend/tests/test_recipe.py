import re
from http import HTTPStatus

import pytest
from pytest_lazyfixture import lazy_fixture
from django.db.models import Q

from api.models import (
    Recipe,
    RecipeIngredients,
    RecipeTags
)
from tests.utils.tag import TAG_SET_SLUGS
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    SCHEMA_PAGINATE,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_FORBIDDEN_ERROR,
    URL_FOUND_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    URL_UNAUTHORIZED_ERROR,
    validate_response_scheme
)
from tests.utils.recipe import (
    BODY_ONLY_POST_BAD_REQUEST,
    BODY_POST_AND_PATH_BAD_REQUESTS,
    BODY_UPDATE_VALID,
    IMAGE,
    SCHEME_RECIPE,
    SCHEME_RECIPE_FIELDS,
    URL_GET_RECIPE,
    URL_GET_SHORT_LINK,
    URL_RECIPES,
    URL_SHORT_LINK
)
from tests.utils.user import SCHEME_USER


@pytest.mark.django_db(transaction=True)
class TestRecipe:

    @pytest.mark.parametrize(
        'subname_test, body', (
            BODY_ONLY_POST_BAD_REQUEST | BODY_POST_AND_PATH_BAD_REQUESTS
        ).items()
    )
    def test_bad_request_method_post(
        self, second_user_authorized_client,
        subname_test, body
    ):
        url = URL_RECIPES
        response = second_user_authorized_client.post(url, body)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=url)
        )

    @pytest.mark.parametrize(
        'subname_test, body', BODY_POST_AND_PATH_BAD_REQUESTS.items()
    )
    def test_bad_request_method_patch(
        self, second_user_authorized_client, first_recipe,
        subname_test, body
    ):
        id_recipe = first_recipe.id
        url = URL_GET_RECIPE.format(id=id_recipe)
        response = second_user_authorized_client.patch(url, body)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=url)
        )

    def test_add_recipe_unauthorized(self, api_client, secound_author_recipes):
        response = api_client.post(URL_RECIPES)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_RECIPES)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=URL_RECIPES)
        )

    def test_update_recipe_unauthorized(self, api_client, first_recipe):
        id_recipe = first_recipe.id
        url = URL_GET_RECIPE.format(id=id_recipe)
        response = api_client.patch(url, BODY_UPDATE_VALID)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=url)
        )

    def test_update_recipe_non_author(
        self, first_user_authorized_client, first_recipe
    ):
        id_recipe = first_recipe.id
        url = URL_GET_RECIPE.format(id=id_recipe)
        response = first_user_authorized_client.patch(url, BODY_UPDATE_VALID)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            URL_FORBIDDEN_ERROR.format(method='patch', url=url)
        )

    def test_update_recipe_none_existing_recipe(
        self, second_user_authorized_client
    ):
        url = URL_GET_RECIPE.format(id=9786)
        response = second_user_authorized_client.patch(url, BODY_UPDATE_VALID)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )

    def test_add_recipe_authorized(
        self, second_user_authorized_client, second_user, ingredients, tags
    ):
        count_recipe = Recipe.objects.count()
        count_recipe_ingredients = RecipeIngredients.objects.count()
        count_recipe_tags = RecipeTags.objects.count()

        body = {
            'ingredients': [
                {'id': ingredient.id, 'amount': 10 + ingredient.id}
                for index, ingredient in enumerate(ingredients)
                if index in (1, 2)
            ],
            'tags': [
                tag.id for index, tag in enumerate(tags) if index in (1, 2)
            ],
            'image': IMAGE,
            'name': 'Новый рецепт',
            'text': 'Забытый рецепт с неизвестными ингредиентами.',
            'cooking_time': 5
        }
        count_body_recipe_ingredients = len(body.get('ingredients'))
        count_body_recipe_tags = len(body.get('tags'))

        response = second_user_authorized_client.post(
            URL_RECIPES,
            data=body
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_RECIPES)
        )
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(method='patch', url=URL_RECIPES)
        )

        new_recipes = Recipe.objects.filter(
            name=body.get('name'),
            text=body.get('text'),
            cooking_time=body.get('cooking_time'))
        assert new_recipes.exists() and new_recipes.count() == (
            count_recipe + 1
        ), (
            'Убедитесь, что рецепт добавился в БД с ожидаемыми полями.'
        )

        id_new_recipe = new_recipes[0].id  # После фильтра кверисет обрубаем
        new_recipe_tags = RecipeTags.objects.filter(
            recipe_id=id_new_recipe,
            tag_id__in=body.get('tags')
        )
        assert new_recipe_tags.exists() and new_recipe_tags.count() == (
            count_recipe_tags + count_body_recipe_tags
        ), (
            'Убедитесь, что в связующую рецепты+теги добавились записи '
            'в БД с ожидаемыми полями.'
        )
        # Для каждого генерим Q-Объект из условия ингры+количества
        query = Q()
        for data in body.get('ingredients'):
            query |= Q(
                recipe_id=id_new_recipe,
                ingredient_id=data['id'],
                amount=data['amount']
            )
        new_recipe_ingredients = RecipeIngredients.objects.filter(query)
        assert (
            new_recipe_ingredients.exists()
            and new_recipe_ingredients.count() == (
                count_recipe_ingredients + count_body_recipe_ingredients
            )
        ), (
            'Убедитесь, что в связующую рецепты+ингредиенты добавились записи '
            'в БД с ожидаемыми полями.'
        )

        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE
        # Для ингров и тегов - списки.
        for field, scheme in SCHEME_RECIPE_FIELDS.items():
            assert validate_response_scheme(
                response_json.get(field)[0], scheme
            ), RESPONSE_PAGINATED_STRUCTURE
        assert validate_response_scheme(
            response_json.get('author'), SCHEME_USER
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_recipes(
        self, client, all_recipes, settings
    ):
        response = client.get(URL_RECIPES)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_RECIPES)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_RECIPES)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_PAGINATE
        ), RESPONSE_PAGINATED_STRUCTURE

        response_count = response_json.get('count', 0)
        assert response_count == len(all_recipes), (
            'Убедитесь, что в count ответа на GET-запрос по адресу '
            f'`{URL_RECIPES}` вернул все рецепты из БД.'
        )
        # TODO: если вдруг падают тесты, нужно использовать проверку:
        # page_size = YourViewSet().pagination_class.page_size
        response_results = response_json.get('results', [])
        page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", None)
        expected_count_results = (
            response_count if response_count < page_size else page_size
        )
        response_results_count = len(response_results)
        assert response_results_count == expected_count_results, (
            f'Убедитесь, что в results отдало {expected_count_results} '
            'объектов. Сейчас вернуло {response_results_count}.'
        )
        response_recipe = response_results[0]
        assert validate_response_scheme(
            response_recipe, SCHEME_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE
        for field, scheme in SCHEME_RECIPE_FIELDS.items():
            assert validate_response_scheme(
                response_recipe.get(field)[0], scheme
            ), RESPONSE_PAGINATED_STRUCTURE
        assert validate_response_scheme(
            response_recipe.get('author'), SCHEME_USER
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize('count', [1, 5, 20])
    def test_get_recipes_paginated(
        self, api_client, secound_author_recipes, count
    ):
        url = URL_RECIPES + '?limit=' + str(count)
        response = api_client.get(url)
        # Проверка на доступность адреса выше
        response_json = response.json()
        response_results = response_json.get('results', [])
        response_results_len = len(response_results)
        recipes_len = len(secound_author_recipes)
        expected_count_results = (
            count if count < recipes_len else recipes_len
        )
        assert response_results_len == expected_count_results, (
            'Убедитесь, что работает пагинация. Получили '
            f'{response_results_len} объектов, ожидали '
            f'{expected_count_results}.'
        )

    @pytest.mark.parametrize(
        'user', [
            lazy_fixture('first_user'),
            lazy_fixture('second_user'),
            lazy_fixture('third_user')
        ]
    )
    def test_get_recipes_filter_by_author(
        self, api_client, all_recipes, settings, user
    ):
        # Интересно, а надо ли фильтр проверить, что именно число?..
        url = URL_RECIPES + '?author=' + str(user.id)
        response_json = api_client.get(url).json().get('results')
        recipe_count = Recipe.objects.filter(
            author_id=user.id
        ).distinct().count()
        page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", None)
        expected_count_results = (
            recipe_count if recipe_count < page_size else page_size
        )
        assert expected_count_results == len(response_json), (
            f'Убедитесь, что по адресу `{URL_RECIPES}` работает '
            'фильтрация по полю author.'
        )

    @pytest.mark.parametrize(
        'count_tags, slug_list', TAG_SET_SLUGS.items()
    )
    def test_get_recipes_filter_by_tags(
        self, api_client, all_recipes, settings, count_tags, slug_list
    ):
        url = URL_RECIPES + '?' + '&'.join(
            [f'tags={slug}' for slug in slug_list]
        )
        response_json = api_client.get(url).json().get('results')
        recipe_count = Recipe.objects.filter(
            tags__slug__in=slug_list
        ).distinct().count()
        page_size = settings.REST_FRAMEWORK.get("PAGE_SIZE", None)
        expected_count_results = (
            recipe_count if recipe_count < page_size else page_size
        )
        assert expected_count_results == len(response_json), (
            f'Убедитесь, что по адресу `{URL_RECIPES}` работает '
            'фильтрация по полю author.'
        )

    @pytest.mark.parametrize(
        'client', [
            lazy_fixture('api_client'),
            lazy_fixture('second_user_authorized_client')
        ]
    )
    def test_get_recipe_detailt(
        self, first_recipe, client
    ):
        url = URL_GET_RECIPE.format(id=first_recipe.id)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_CREATED_ERROR.format(method='patch', url=url)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE
        for field, scheme in SCHEME_RECIPE_FIELDS.items():
            assert validate_response_scheme(
                response_json.get(field)[0], scheme
            ), RESPONSE_PAGINATED_STRUCTURE
        assert validate_response_scheme(
            response_json.get('author'), SCHEME_USER
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize(
        'client', [
            lazy_fixture('api_client'),
            lazy_fixture('second_user_authorized_client')
        ]
    )
    @pytest.mark.parametrize(
        'recipe', [
            lazy_fixture('first_recipe'),
            lazy_fixture('third_recipe'),
            lazy_fixture('fifth_recipe')
        ]
    )
    def test_get_short_link(
        self, recipe, client
    ):
        url = URL_GET_SHORT_LINK.format(id=recipe.id)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_CREATED_ERROR.format(method='patch', url=url)
        )
        response_json = response.json()
        short_link = response_json.get('short-link', '')
        pattern = r'^.*/s/[a-zA-Z0-9]{2,6}$'
        assert re.match(pattern, short_link) is not None, (
            'Убедитесь, что в ответе запроса на адрес `{url}` значение '
            '`short_link` соответствует регулярному выражению `{pattern}`.'
        )

    @pytest.mark.parametrize(
        'client', [
            lazy_fixture('api_client'),
            lazy_fixture('second_user_authorized_client')
        ]
    )
    @pytest.mark.parametrize(
        'recipe', [
            lazy_fixture('second_recipe'),
            lazy_fixture('fourth_recipe'),
            lazy_fixture('another_author_recipe')
        ]
    )
    def test_redirect_short_link(
        self, recipe, client
    ):
        url = URL_SHORT_LINK.format(uuid=recipe.short_link)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.FOUND, (
            URL_FOUND_ERROR.format(method='patch', url=url)
        )
        redirect_url = response.headers.get('Location')
        expected_redirect_url = URL_GET_RECIPE.format(id=recipe.id)
        assert redirect_url == expected_redirect_url, (
            f'Проверьте, что адрес `{url}` перенаправляет на '
            f'`{expected_redirect_url}`. На текущий момент перенаправляет на '
            f'`{redirect_url}`.'
        )

    def test_update_recipe_author(
        self, second_user_authorized_client, first_recipe, tags, ingredients
    ):
        url = URL_GET_RECIPE.format(id=first_recipe.id)
        # Из-за боли с транзакциями делаем немного махинаций
        body = BODY_UPDATE_VALID.copy()
        body['tags'] = [
            tags[id].id for id in body['tags']
        ]
        for ingredient in body['ingredients']:
            ingredient['id'] = ingredients[ingredient['id']].id

        response = second_user_authorized_client.patch(url, body)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_CREATED_ERROR.format(method='patch', url=url)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_RECIPE
        ), RESPONSE_PAGINATED_STRUCTURE
        # Для ингров и тегов - списки.
        for field, scheme in SCHEME_RECIPE_FIELDS.items():
            assert validate_response_scheme(
                response_json.get(field)[0], scheme
            ), RESPONSE_PAGINATED_STRUCTURE
        assert validate_response_scheme(
            response_json.get('author'), SCHEME_USER
        ), RESPONSE_PAGINATED_STRUCTURE

        recipes = Recipe.objects.filter(
            name=body.get('name'),
            text=body.get('text'),
            cooking_time=body.get('cooking_time'))
        assert recipes.exists(), (
            'Убедитесь, что поля в рецепте обновились.'
        )
        id_recipe = recipes[0].id
        recipe_tags = RecipeTags.objects.filter(
            recipe_id=id_recipe,
            tag_id__in=body.get('tags')
        )
        assert (
            recipe_tags.exists()
            and recipe_tags.count() == len(body.get('tags'))
        ), (
            'Убедитесь, что в связующей рецепты+теги только обновленные записи'
        )
        query = Q()
        for data in body.get('ingredients'):
            query |= Q(
                recipe_id=id_recipe,
                ingredient_id=data['id'],
                amount=data['amount']
            )
        recipe_ingredients = RecipeIngredients.objects.filter(query)
        assert (
            recipe_ingredients.exists()
            and recipe_ingredients.count() == len(
                body.get('ingredients')
            )
        ), (
            'Убедитесь, что в связующей рецепты+ингредиенты только '
            'обновленные записи'
        )
