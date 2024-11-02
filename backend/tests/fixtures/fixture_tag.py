import pytest

from api.models.tag import Tag
from tests.utils.tag import TAG_DATA


@pytest.fixture
def tags():
    tags = [Tag(**item) for item in TAG_DATA]
    Tag.objects.bulk_create(tags)
    return list(Tag.objects.all())
