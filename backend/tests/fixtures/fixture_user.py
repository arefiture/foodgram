import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.utils.user import (
    FIRST_VALID_USER,
    SECOND_VALID_USER,
    THIRD_VALID_USER
)

User = get_user_model()


def create_user(django_user_model, user_data):
    return django_user_model.objects.create_user(
        **user_data
    )


def get_user_token(user, password):
    client = APIClient()
    response = client.post('/api/auth/token/login/', {
        'email': user.email,
        'password': password
    })
    token = response.data.get('auth_token')
    return {
        'auth_token': token
    }


def authorized_client(token):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token["auth_token"]}'
    )
    return client


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def first_user(django_user_model):
    return create_user(django_user_model, FIRST_VALID_USER)


@pytest.fixture
def second_user(django_user_model):
    return create_user(django_user_model, SECOND_VALID_USER)


@pytest.fixture
def third_user(django_user_model):
    return create_user(django_user_model, THIRD_VALID_USER)


@pytest.fixture
def all_user(first_user, second_user, third_user):
    return [first_user, second_user, third_user]


@pytest.fixture
def first_user_token(first_user):
    return get_user_token(
        user=first_user, password=FIRST_VALID_USER['password']
    )


@pytest.fixture
def second_user_token(second_user):
    return get_user_token(
        user=second_user, password=SECOND_VALID_USER['password']
    )


@pytest.fixture
def first_user_authorized_client(first_user_token):
    return authorized_client(token=first_user_token)


@pytest.fixture
def second_user_authorized_client(second_user_token):
    return authorized_client(token=second_user_token)
