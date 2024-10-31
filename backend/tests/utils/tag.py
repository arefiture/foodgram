from tests.utils.general import (
    CHANGE_METHOD,
    installation_method_urls
)

# Адреса страниц
URL_TAGS = '/api/tags/'
URL_GET_TAG = '/api/tags/{id}/'

# Структуры для перебора
TAG_DATA = [
    {'name': 'Десерт', 'slug': 'dessert'},
    {'name': 'Завтрак', 'slug': 'breakfast'},
    {'name': 'Обед', 'slug': 'lunch'},
    {'name': 'Ужин', 'slug': 'dinner'}
]

DENY_CHANGE_METHOD = installation_method_urls(
    url=URL_TAGS,
    url_detail=URL_GET_TAG.format(id=1),
    dict_method_urls=CHANGE_METHOD
)

# Схемы валидации данных в ответах методов
SCHEME_TAG = {
    'id': (int, ),
    'name': (str, ),
    'slug': (str, )
}
