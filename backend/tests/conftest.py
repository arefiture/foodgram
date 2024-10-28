import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.utils import FIRST_VALID_USER

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def first_user(django_user_model):
    return django_user_model.objects.create_user(
        **FIRST_VALID_USER
    )


@pytest.fixture
def token_first_user(first_user):
    client = APIClient()
    response = client.post('/api/auth/token/login/', {
        'email': first_user.email,
        'password': FIRST_VALID_USER['password']
    })
    token = response.data.get('auth_token')
    return {
        'auth_token': token
    }


@pytest.fixture
def authorized_client_for_first_user(token_first_user):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token_first_user["auth_token"]}'
    )
    return client
