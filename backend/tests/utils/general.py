# Обязательность полей
RESPONSE_KEY_ERROR_FIELD = 'non_field_errors'
REQUIRED_FIELDS_ERROR = (
    'Если в POST-запросе к `{url}` не переданы необходимые данные, '
    'в ответе должна возвращаться информация об обязательных для '
    'заполнения полях.'
)

# Описание ошибок по статусам
URL_BAD_REQUEST_ERROR = (
    'Если POST-запрос, отправленный на эндпоинт `{url}`, '
    'не содержит необходимых данных, должен вернуться ответ со '
    'статусом 400.'
)
URL_CREATED_ERROR = (
    'Проверьте, что POST-запрос к `{url}` с корректными '
    'возвращает статус-код 201.'
)
URL_NOT_FOUND_ERROR = (
    'Эндпоинт `{url}` не найден. Проверьте настройки в *urls.py*.'
)
URL_NO_CONTENT_ERROR = (
    'Проверьте, что POST-запрос зарегистрированного пользователя к '
    '`{url}`возвращает статус-код 204.'
)
URL_OK_ERROR = (
    'Проверьте, что POST-запрос к `{url}` с корректными возвращает '
    'статус-код 200.'
)
URL_UNAUTHORIZED_ERROR = (
    'Проверьте, что POST-запрос анонимного пользователя к '
    '`{url}`возвращает статус-код 401.'
)

# Иные ошибки ответов
RESPONSE_EXPECTED_STRUCTURE = (
    'Структура ответа должна соответствовать ожидаемой.'
)
RESPONSE_PAGINATED_STRUCTURE = (
    'Убедитесь, что для запрошенного эндпоинта настроена пагинация.'
)

# Схемы валидации данных в ответах методов
SCHEMA_PAGINATE = {
    'count': (int, ),
    'next': (str, type(None)),
    'previous': (str, type(None)),
    'results': (list, )
}


# Вспомогательные функции
def validate_response_schema(response_json, schema):
    for field, types in schema.items():
        if not (
            field in response_json
            or isinstance(response_json[field], types)
        ):
            return False
    return True
