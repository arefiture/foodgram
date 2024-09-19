from uuid import uuid4


def generate_short_link():
    return uuid4().hex[:6]
