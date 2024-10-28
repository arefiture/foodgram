# TODO: попробовать разбить константы в рамках пакета по тест-классам

# POSTMAN-константы
USERNAME = 'vasya.ivanov'
PASSWORD = 'MySecretPas$word'
EMAIL = 'vivanov@yandex.ru'
TOO_LONG_EMAIL = (
    'i_have_never_seen_an_email_address_longer_than_two_hundred_and_fifty_'
    'four_characters_and_it_was_difficult_to_come_up_with_it_so_in_the_'
    'second_part_just_the_names_of_some_mail_services@yandex-google-yahoo-'
    'mailgun-protonmail-mailru-outlook-icloud-aol-neo.ru'
)
TOO_LONG_USERNAME = (
    'the-username-that-is-150-characters-long-and-should-not-pass-validation-'
    'if-the-serializer-is-configured-correctly-otherwise-the-current-test-'
    'will-fail-'
)
NEW_PASSWORD = 'thi$Pa$$w0rdW@sCh@nged'
FIRST_INGREDIENT_AMOUNT = 10
SECOND_INGREDIENT_AMOUNT = 20
SECOND_USER_USERNAME = 'second-user'
SECOND_USER_EMAIL = 'second_user@email.org'
THIRD_USER_USERNAME = 'third-user'
THIRD_USER_EMAIL = 'third-user@user.ru'

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
    'Проверьте, что POST-запрос к `{url}` '
    'с корректными возвращает статус-код 200.'
)
URL_UNAUTHORIZED_ERROR = (
    'Проверьте, что POST-запрос анонимного пользователя к '
    '`{url}`возвращает статус-код 401.'
)

# Иные ошибки ответов
RESPONSE_EXPECTED_STRUCTURE = (
    'Структура ответа должна соответствовать ожидаемой.'
)

# Структуры для обхода
INVALID_USER_DATA_FOR_LOGIN = [
    {
        'email': SECOND_USER_USERNAME,
        'password': 'randomPassword'
    },
    {
        'password': PASSWORD
    },
    {
        'email': SECOND_USER_USERNAME
    }
]

INVALID_USER_DATA_FOR_REGISTER = [
    {
        'username': 'NoEmail',
        'first_name': 'No',
        'last_name': 'Email',
        'password': PASSWORD
    },
    {
        'email': 'no-username@user.ru',
        'first_name': 'Username',
        'last_name': 'NotProvided',
        'password': PASSWORD
    },
    {
        'username': 'NoFirstName',
        'email': 'no-first-name@user.ru',
        'last_name': 'NoFirstName',
        'password': PASSWORD
    },
    {
        'username': 'NoLastName',
        'email': 'no-last-name@user.ru',
        'first_name': 'NoLastName',
        'password': PASSWORD
    },
    {
        'username': 'NoPassword',
        'email': 'no-pasword@user.ru',
        'first_name': 'NoPassword',
        'last_name': 'NoPassword'
    },
    {
        'username': 'TooLongEmail',
        'email': TOO_LONG_EMAIL,
        'first_name': 'TooLongEmail',
        'last_name': 'TooLongEmail',
        'password': PASSWORD
    },
    {
        'username': TOO_LONG_USERNAME,
        'email': 'too-long-username@user.ru',
        'first_name': 'TooLongUsername',
        'last_name': 'TooLongUsername',
        'password': PASSWORD
    },
    {
        'username': 'TooLongFirstName',
        'email': 'too-long-firt-name@user.ru',
        'first_name': TOO_LONG_USERNAME,
        'last_name': 'TooLongFirstName',
        'password': PASSWORD
    },
    {
        'username': 'TooLongLastName',
        'email': 'too-long-last-name@user.ru',
        'first_name': 'TooLongLastName',
        'last_name': TOO_LONG_USERNAME,
        'password': PASSWORD
    },
    {
        'username': 'InvalidU$ername',
        'email': 'invalid-username@user.ru',
        'first_name': 'Invalid',
        'last_name': 'Username',
        'password': PASSWORD
    }
]

IN_USE_USER_DATA_FOR_REGISTER = [
    {
        'email': EMAIL,
        'username': 'EmailInUse',
        'first_name': 'Email',
        'last_name': 'InUse',
        'password': PASSWORD,
        'assert_msg': (
            'Если POST-запрос, отправленный на эндпоинт `{url}`, '
            'содержит `email` зарегистрированного пользователя и незанятый '
            '`username` - должен вернуться ответ со статусом 400.'
        )
    },
    {
        'email': 'username-in-use@user.ru',
        'username': USERNAME,
        'first_name': 'Username',
        'last_name': 'InUse',
        'password': PASSWORD,
        'assert_msg': (
            'Если POST-запрос, отправленный на эндпоинт `{url}`, '
            'содержит `username` зарегистрированного пользователя и '
            'несоответствующий ему `email` - должен вернуться ответ со '
            'статусом 400.'
        )
    }
]

FIRST_VALID_USER = {
    'email': EMAIL,
    'username': USERNAME,
    'first_name': 'Вася',
    'last_name': 'Иванов',
    'password': PASSWORD
}

SECOND_VALID_USER = {
    "email": SECOND_USER_EMAIL,
    "username": SECOND_USER_USERNAME,
    "first_name": "Андрей",
    "last_name": "Макаревский",
    "password": PASSWORD
}

THIRD_VALID_USER = {
    "email": THIRD_USER_EMAIL,
    "username": THIRD_USER_USERNAME,
    "first_name": "Гордон",
    "last_name": "Рамзиков",
    "password": PASSWORD
}
