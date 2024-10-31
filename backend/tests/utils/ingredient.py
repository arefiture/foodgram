from tests.utils.general import (
    CHANGE_METHOD,
    installation_method_urls
)

# Адреса страниц
URL_INGREDIENTS = '/api/ingredients/'
URL_GET_INGREDIENT = '/api/ingredients/{id}/'

# Структуры для перебора
INGREDIENT_DATA = [
    {'name': 'абрикосовое варенье', 'measurement_unit': 'г'},
    {'name': 'абрикосовое пюре', 'measurement_unit': 'г'},
    {'name': 'апельсиновая вода', 'measurement_unit': 'мл'},
    {'name': 'булочки зерновые', 'measurement_unit': 'шт'}
]
INGREDIENT_SEARCH_DATA = [
    'а', 'б', 'аб', 'ба'
]


DENY_CHANGE_METHOD = installation_method_urls(
    url=URL_INGREDIENTS,
    url_detail=URL_GET_INGREDIENT.format(id=1),
    dict_method_urls=CHANGE_METHOD
)

# Схемы валидации данных в ответах методов
SCHEME_INGREDIENT = {
    'id': (int, ),
    'name': (str, ),
    'measurement_unit': (str, )
}
