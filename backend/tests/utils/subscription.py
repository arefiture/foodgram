from tests.utils.user import URL_CREATE_USER, URL_GET_USER

# Адреса страниц
URL_CREATE_SUBSCRIBE = URL_GET_USER + 'subscribe/'
URL_GET_SUBSCRIPTIONS = URL_CREATE_USER + 'subscriptions/'

# Схемы валидации данных в ответах методов
SCHEME_SUBSCRIPTION = {
    'id': (int, ),
    'username': (str, ),
    'first_name': (str, ),
    'last_name': (str, ),
    'email': (str, ),
    'is_subscribed': (bool, ),
    'avatar': (str, type(None)),
    'recipes_count': (int, ),
    'recipes': (list, )
}
SCHEME_SUBSCRIPTION_RECIPE = {
    'id': (int, ),
    'name': (str, ),
    'image': (str, ),
    'cooking_time': (int, )
}
