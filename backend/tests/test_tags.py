from http import HTTPStatus

import pytest

from api.models.tag import Tag
from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    URL_METHOD_NOT_ALLOWED,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    validate_response_schema,
)
from tests.utils.tag import (
    SHEMA_TAG,
    URL_GET_TAG,
    URL_TAGS,
    DENY_CHANGE_METHOD
)


@pytest.mark.django_db(transaction=True)
class TestTags:

    @pytest.mark.parametrize('change_metod', DENY_CHANGE_METHOD)
    def test_bad_request_methods(
        self, first_user_authorized_client, tags, change_metod
    ):
        url = change_metod['url']
        method = change_metod['method']
        response = getattr(first_user_authorized_client, method)(url)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            URL_METHOD_NOT_ALLOWED.format(method=method.upper(), url=url)
        )

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_tags(
        self, client, tags
    ):
        response = client.get(URL_TAGS)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=URL_TAGS)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=URL_TAGS)
        )
        response_json = response.json()
        assert isinstance(response_json, list) and validate_response_schema(
            response_json[0], SHEMA_TAG
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_tag_detail(self, client, tags):
        id_tag = Tag.objects.first().id
        url = URL_GET_TAG.format(id=id_tag)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=url)
        )
        response_json = response.json()
        assert validate_response_schema(
            response_json, SHEMA_TAG
        ), RESPONSE_PAGINATED_STRUCTURE

    def test_non_existing_tag(self, client, tags):
        id_tag = max(item['id'] for item in Tag.objects.values('id'))
        url = URL_GET_TAG.format(id=id_tag + 1)
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
