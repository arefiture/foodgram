from rest_framework.exceptions import ValidationError


class SubscribeUniqueValidator:
    """
    Валидатор для сравнения подписчика и автора.

    В случае если они равны вызывает исключение, т.к.
    подпись на самого себя не имеет смысла.
    """
    message = 'Невозможно подписаться на самого себя'

    def __init__(self, fields, message=None):
        self.fields = fields
        self.message = message or self.message

    def __call__(self, attrs):
        follower = attrs.get('follower')
        followed = attrs.get('followed')

        if follower == followed:
            raise ValidationError(self.message)
