import re
from http import HTTPStatus

import pytest

from tests.utils.general import (
    RESPONSE_EXPECTED_STRUCTURE,
    RESPONSE_PAGINATED_STRUCTURE,
    SCHEMA_PAGINATE,
    URL_NO_CONTENT_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    URL_UNAUTHORIZED_ERROR,
    validate_response_scheme,
)
from tests.utils.user import (
    AVATAR,
    FIRST_VALID_USER,
    NEW_PASSWORD,
    SCHEMA_ADDED_AVATAR,
    SCHEMA_USER,
    URL_AVATAR,
    URL_CREATE_USER,
    URL_GET_USER,
    URL_LOGIN,
    URL_ME,
    URL_SET_PASSWORD,
)


@pytest.mark.django_db(transaction=True)
class TestUsers:
    UNAUTHORIZED_BANNED_METHODS = {
        'post_me': {'url': URL_ME, 'method': 'post'},
        'put_avatar': {'url': URL_AVATAR, 'method': 'put'},
        'delete_avatar': {'url': URL_AVATAR, 'method': 'delete'},
        'post_set_password': {'url': URL_SET_PASSWORD, 'method': 'post'},
    }

    @pytest.mark.parametrize(
        'method_name, data', UNAUTHORIZED_BANNED_METHODS.items()
    )
    def test_bad_request_unauthorized(self, api_client, method_name, data):
        url = data['url']
        response = getattr(api_client, data['method'])(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=url)
        )

    def test_non_existing_profile(
        self, api_client, django_user_model, all_user
    ):
        max_id = max(element.id for element in django_user_model.objects.all())
        response = api_client.get(URL_GET_USER.format(id=max_id + 1))
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_GET_USER)
        )

    def test_reset_password_wrong_data(
        self, first_user_authorized_client, first_user, django_user_model
    ):
        old_password = first_user.password
        response = first_user_authorized_client.post(URL_SET_PASSWORD, {
            'current_password': 'wrongPassword',
            'new_password': NEW_PASSWORD
        })
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_SET_PASSWORD)
        )
        invalid_field = 'current_password'
        response_json = response.json()
        assert (invalid_field in response_json
                and isinstance(response_json.get(invalid_field), list)), (
            f'Если в POST-метод к `{URL_SET_PASSWORD}` передан неверный '
            'пароль, в ответе должна быть соответствующая информация.'
        )
        assert (old_password == django_user_model
                .objects.get(id=first_user.id).password), (
            'Убедитесь, что при неверном текущем пароле данные в БД '
            'будут без изменений.'
        )

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_users(self, client, all_user):
        response = client.get(URL_CREATE_USER)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_CREATE_USER)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_CREATE_USER)
        )

        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_PAGINATE
        ), RESPONSE_PAGINATED_STRUCTURE
        response_count = response_json['count']
        assert len(all_user) == response_count, (
            'Убедитесь, что в count ответа приходит число всех записей, '
            'существующих в БД.'
        )

        response_results_json = response_json.get('results')
        assert validate_response_scheme(
            response_results_json[0], SCHEMA_USER
        ), RESPONSE_EXPECTED_STRUCTURE

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_user_detail(self, client, all_user):
        user_id = all_user[0].id
        url = URL_GET_USER.format(id=user_id)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=url)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_USER
        ), RESPONSE_EXPECTED_STRUCTURE

    @pytest.mark.parametrize('limit', [1, 999999])
    def test_get_users_paginated(
        self, first_user_authorized_client, all_user, limit
    ):
        # Структура и доступность проверялись выше
        url = URL_CREATE_USER + '?limit=' + str(limit)
        response = first_user_authorized_client.get(url)
        response_json = response.json()
        count_db = response_json['count']
        count_results = len(response_json['results'])
        if count_db <= limit:
            assert count_db == count_results, (
                'При count <= limit требуется отобразить все записи.'
            )
        else:
            assert limit == count_results, (
                f'Должно отобразиться {limit} элементов, отобразилось '
                f'{count_results} элементов.'
            )

    def test_get_users_me(
        self, first_user_authorized_client, all_user
    ):
        response = first_user_authorized_client.get(URL_ME)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_ME)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_ME)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_USER
        ), RESPONSE_EXPECTED_STRUCTURE
        is_subscribed = response_json['is_subscribed']
        assert not is_subscribed, (
            f'Для {URL_ME} ожидалось, что is_subscribed будет False. '
            f'Получено значение {is_subscribed}.'
        )

    def test_put_users_me_avatar(
        self, first_user_authorized_client, first_user, django_user_model
    ):
        old_avatar = (
            django_user_model.objects.get(id=first_user.id).avatar.name
        )
        response = first_user_authorized_client.put(URL_AVATAR, {
            'avatar': AVATAR
        })
        new_avatar = (
            django_user_model.objects.get(id=first_user.id).avatar.name
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_AVATAR)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_AVATAR)
        )
        assert old_avatar != new_avatar, (
            'Поле avatar в БД должно обновиться.'
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEMA_ADDED_AVATAR
        ), RESPONSE_EXPECTED_STRUCTURE

        response = first_user_authorized_client.get(URL_ME)
        avatar_url = response_json.get('avatar')
        assert avatar_url is not None, (
            'После добавления аватара должна возвращаться ссылка на него.'
        )
        pattern_avatar = r'^https?://[a-zA-Z0-9.-]+/media/users/[\w-]+\.png$'
        assert bool(re.match(pattern_avatar, avatar_url)), (
            RESPONSE_EXPECTED_STRUCTURE
        )

    def test_delete_me_avatar_authorized(
        self, second_user_authorized_client, second_user, django_user_model
    ):
        old_avatar = (
            django_user_model.objects.get(id=second_user.id).avatar.name
        )
        response = second_user_authorized_client.delete(URL_AVATAR)
        new_avatar = (
            django_user_model.objects.get(id=second_user.id).avatar.name
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_AVATAR)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            URL_NO_CONTENT_ERROR.format(url=URL_AVATAR)
        )
        assert old_avatar != new_avatar, (
            'Поле avatar в БД должно стать пустым.'
        )

        response = second_user_authorized_client.get(URL_ME)
        response_json = response.json()
        avatar_url = response_json.get('avatar')
        assert avatar_url is None, (
            'Убедитесь, что после корректного запроса на удаление аватара в '
            'ответе на запрос к данным пользователя в поле `avatar` вернётся '
            '`null` или пустая строка'
        )

    def test_reset_password(
        self, first_user_authorized_client, first_user, django_user_model
    ):
        old_password = first_user.password
        response = first_user_authorized_client.post(URL_SET_PASSWORD, {
            'current_password': FIRST_VALID_USER['password'],
            'new_password': NEW_PASSWORD
        })
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_AVATAR)
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            URL_NO_CONTENT_ERROR.format(url=URL_AVATAR)
        )
        assert (old_password != django_user_model
                .objects.get(id=first_user.id).password), (
            'Убедитесь, что при корректном текущем пароле данные в БД '
            'будут изменены.'
        )

        response = first_user_authorized_client.post(URL_LOGIN, {
            'password': NEW_PASSWORD,
            'email': first_user.email
        })
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_AVATAR)
        )
