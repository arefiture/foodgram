from http import HTTPStatus

import pytest

from tests.utils.general import (
    RESPONSE_PAGINATED_STRUCTURE,
    URL_METHOD_NOT_ALLOWED,
    URL_NOT_FOUND_ERROR,
    URL_OK_ERROR,
    validate_response_scheme,
)
from tests.utils.tag import (
    SCHEME_TAG,
    URL_GET_TAG,
    URL_TAGS,
    DENY_CHANGE_METHOD
)


@pytest.mark.django_db(transaction=True)
class TestTags:

    @pytest.mark.parametrize(
        'method, method_info', DENY_CHANGE_METHOD.items()
    )
    def test_bad_request_methods(
        self, first_user_authorized_client, tags, method, method_info
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
        assert isinstance(response_json, list) and validate_response_scheme(
            response_json[0], SCHEME_TAG
        ), RESPONSE_PAGINATED_STRUCTURE

    @pytest.mark.parametrize(
        'client',
        ['api_client', 'first_user_authorized_client'],
        indirect=True
    )
    def test_get_tag_detail(self, client, tags):
        id_tag = tags[0].id
        url = URL_GET_TAG.format(id=id_tag)
        response = client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
        assert response.status_code == HTTPStatus.OK, (
            URL_OK_ERROR.format(url=url)
        )
        response_json = response.json()
        assert validate_response_scheme(
            response_json, SCHEME_TAG
        ), RESPONSE_PAGINATED_STRUCTURE

    def test_non_existing_tag(self, client, tags):
        id_tag = max(tag.id for tag in tags)
        url = URL_GET_TAG.format(id=id_tag + 1)
        response = client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            URL_NOT_FOUND_ERROR.format(url=url)
        )
