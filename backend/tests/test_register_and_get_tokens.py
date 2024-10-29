from http import HTTPStatus

from django.db import IntegrityError
import pytest

from tests.utils.users import (
    FIRST_VALID_USER,
    IN_USE_USER_DATA_FOR_REGISTER,
    INVALID_USER_DATA_FOR_LOGIN,
    INVALID_USER_DATA_FOR_REGISTER,
    SECOND_VALID_USER,
    THIRD_VALID_USER,
    URL_CREATE_USER,
    URL_LOGIN,
    URL_LOGOUT
)
from tests.utils.general import (
    REQUIRED_FIELDS_ERROR,
    RESPONSE_EXPECTED_STRUCTURE,
    RESPONSE_KEY_ERROR_FIELD,
    URL_BAD_REQUEST_ERROR,
    URL_CREATED_ERROR,
    URL_NOT_FOUND_ERROR,
    URL_NO_CONTENT_ERROR,
    URL_OK_ERROR,
    URL_UNAUTHORIZED_ERROR,
)


@pytest.mark.django_db(transaction=True)
class TestUserRegistration:

    def check_invalid_data_signup(self, response):
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_LOGIN)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=URL_LOGIN)
        )
        response_json = response.json()
        assert RESPONSE_KEY_ERROR_FIELD in response_json, (
            REQUIRED_FIELDS_ERROR.format(url=URL_LOGIN)
        )

    def test_nodata_signup(self, api_client):
        response = api_client.post(URL_LOGIN)
        self.check_invalid_data_signup(response=response)

    @pytest.mark.parametrize('user_data', INVALID_USER_DATA_FOR_LOGIN)
    def test_invalid_data_signup(self, api_client, user_data):
        response = api_client.post(URL_LOGIN, data=user_data)
        self.check_invalid_data_signup(response=response)

    @pytest.mark.parametrize('user_data', INVALID_USER_DATA_FOR_REGISTER)
    def test_without_data_register(self, api_client, user_data):
        url = URL_CREATE_USER
        response = api_client.post(url, user_data)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            URL_BAD_REQUEST_ERROR.format(url=url)
        )
        # Пример: {'email': ['Обязательное поле']}
        response_json = response.json()
        empty_fields = [
            'email', 'username', 'first_name', 'last_name', 'password'
        ]
        for field in response_json:
            assert (field in empty_fields
                    and isinstance(response_json.get(field), list)), (
                f'Если в POST-запросе к `{url}` не переданы '
                'необходимые данные, в ответе должна возвращаться информация '
                'об обязательных для заполнения полях.'
            )

    def check_create_user(self, api_client, model, data):
        url = URL_CREATE_USER
        user_count = model.objects.count()
        response = api_client.post(url, data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            URL_CREATED_ERROR.format(url=url)
        )
        response_json = response.json()
        response_field = {'id', 'email', 'username', 'first_name', 'last_name'}
        assert set(response_json.keys()) == response_field, (
            RESPONSE_EXPECTED_STRUCTURE
        )
        user_count += 1
        assert user_count == model.objects.count(), (
            'При корректных данных должен создаваться новый пользователь.'
        )

    @pytest.mark.parametrize('user_data', IN_USE_USER_DATA_FOR_REGISTER)
    def test_in_use_data_register(
        self, api_client, django_user_model, user_data
    ):
        self.check_create_user(api_client, django_user_model, user_data)

        url = URL_CREATE_USER
        user_count = django_user_model.objects.count()
        assert_msg = user_data.pop('assert_msg').format(url=url)
        try:
            response = api_client.post(url, data=user_data)
        except IntegrityError:
            raise AssertionError(assert_msg)
        assert response.status_code == HTTPStatus.BAD_REQUEST, (assert_msg)
        assert user_count == django_user_model.objects.count(), (
            'При занятых уникальных полях не должен создаваться пользователь.'
        )

    @pytest.mark.parametrize(
        'user_data', [FIRST_VALID_USER, SECOND_VALID_USER, THIRD_VALID_USER]
    )
    def test_signup(self, api_client, django_user_model, user_data):
        self.check_create_user(api_client, django_user_model, user_data)

        response = api_client.post(URL_LOGIN, {
            key: value for key, value in user_data.items()
            if key in ('email', 'password')
        })
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_LOGIN)
        )
        response_json = response.json()
        assert set(response_json.keys()) == {'auth_token', }, (
            RESPONSE_EXPECTED_STRUCTURE
        )

    def test_logout_authorized_client(self, first_user_authorized_client):
        response = first_user_authorized_client.post(
            URL_LOGOUT
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            URL_NO_CONTENT_ERROR.format(url=URL_LOGOUT)
        )

    def test_logout_unauthorized_client(self, api_client):
        response = api_client.post(URL_LOGOUT)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            URL_UNAUTHORIZED_ERROR.format(url=URL_LOGOUT)
        )
