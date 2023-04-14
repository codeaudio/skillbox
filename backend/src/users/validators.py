from re import fullmatch

from django.core.exceptions import ValidationError


def username_validator(value: str) -> str:
    if fullmatch(r'[a-zA-Z]+', value):
        return value

    raise ValidationError(
        'В username может использоваться только латиница'
    )


def password_validator(value: str) -> str:
    if fullmatch(r'[a-zA-Z0-9]{8,}', value):
        return value

    raise ValidationError(
        'В password может использоваться только латиница,'
        ' цифры и минимальная длина 8  символов'
    )
