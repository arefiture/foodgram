from tests.utils.ingredient import SCHEME_INGREDIENT
from tests.utils.tag import SCHEME_TAG

# Константы из postman
IMAGE = (
    'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywa'
    'AAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQV'
    'QImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=='
)

# Адреса страниц
URL_RECIPES = '/api/recipes/'
URL_GET_RECIPE = '/api/recipes/{id}/'
URL_GET_SHORT_LINK = '/api/recipes/{id}/get-link/'
URL_SHORT_LINK = '/s/{uuid}/'

# Структуры для перебора
_INGREDIENTS = [
    {'id': 1, 'amount': 10},
    {'id': 2, 'amount': 20}
]
_TAGS = [1, 2]
_NAME = 'Пример невалидного рецепта'
_TEXT = 'Чисто для тестов.'
_COOKING_TIME = 90

BODY_UPDATE_VALID = {
    'ingredients': [{'id': 1, 'amount': 15}],
    'tags': [1, 2, 3],
    'image': IMAGE,
    'name': 'Обновленный рецепт',
    'text': 'Проверка обновления.',
    'cooking_time': 15
}

BODY_POST_AND_PATH_BAD_REQUESTS = {
    'without_ingredients': {
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'without_tags': {
        'ingredients': _INGREDIENTS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'empty_ingredients': {
        'ingredients': [],
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'empty_tags': {
        'ingredients': _INGREDIENTS,
        'tags': [],
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'empty_image': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': '',
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'empty_name': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': '',
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'empty_text': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': '',
        'cooking_time': _COOKING_TIME
    },
    'empty_string_as_cooking_time': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': ''
    },
    'non_existing_ingredients': {
        'ingredients': [{'id': 9876, 'amount': 25}],
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'non_existing_tags': {
        'ingredients': _INGREDIENTS,
        'tags': [9876],
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'repetitive_ingredients': {
        'ingredients': [
            {'id': 1, 'amount': 10},
            {'id': 1, 'amount': 20},
        ],
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'repetitive_tags': {
        'ingredients': _INGREDIENTS,
        'tags': [1, 1],
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'ingredients_amount_less_than_one': {
        'ingredients': [{'id': 1, 'amount': 0}],
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'cooking_time_less_than_one': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': 0
    },
    'too_long_name': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': (
            'Старинный рецепт, передаваемый из поколения в поколение через '
            'сказки и народные предания. Немногие могут правильно его '
            'приготовить. Большая сложность обусловлена названием, которое '
            'длиннее 256 символов, что существенно усложняет его '
            'запоминание. Дерзайте!!!'
        ),
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    }
}
BODY_ONLY_POST_BAD_REQUEST = {
    'without_image': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'name': _NAME,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'without_name': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'text': _TEXT,
        'cooking_time': _COOKING_TIME
    },
    'without_text_field': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'cooking_time': _COOKING_TIME
    },
    'without_cooking_time': {
        'ingredients': _INGREDIENTS,
        'tags': _TAGS,
        'image': IMAGE,
        'name': _NAME,
        'text': _TEXT,
    }
}

# Схемы валидации данных в ответах методов
SCHEME_SHORT_RECIPE = {
    'id': (int, ),
    'name': (str, ),
    'image': (str, ),
    'cooking_time': (int, )
}

SCHEME_RECIPE = {
    'id': (int, ),
    'tags': (list, ),
    'author': (dict, ),
    'ingredients': (list, ),
    'is_favorited': (bool, ),
    'is_in_shopping_cart': (bool, ),
    'name': (str, ),
    'image': (str, ),
    'text': (str, ),
    'cooking_time': (int, )
}

SCHEME_RECIPE_INGREDIENT = SCHEME_INGREDIENT | {
    'amount': (int, ),
}

SCHEME_RECIPE_FIELDS = {
    'ingredients': SCHEME_RECIPE_INGREDIENT,
    'tags': SCHEME_TAG
}
