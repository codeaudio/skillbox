from django.db import IntegrityError
from django.utils.crypto import get_random_string
from rest_framework.exceptions import APIException

from services.dto import Email
from services.email_service import EmailType, send_email
from users.models import AuthCode, ConfirmCode, User


def generate_confirm_code() -> str:
    """

    Returns
    -------
    random_string :
        рандомная строка из 32 символов
    """
    return get_random_string(32)


def create_confirm_code(user: User) -> AuthCode:
    """
    Parameters
    ----------
    user :
        объект модели пользователя
    Returns
    -------
    ConfirmCode :
        объект модели ConfirmCode
    Raises
    -------
    APIException
    """
    try:
        return ConfirmCode.objects.create(
            code=generate_confirm_code(),
            user=user
        )
    except IntegrityError:
        raise APIException(detail='Код подтверждения уже был создан')


def send_confirm(user: User) -> None:
    """
    Parameters
    ----------
    user :
        объект модели пользователя
    Raises
    -------
    APIException
    """
    confirm_code = create_confirm_code(user)

    try:
        send_email(
            email_data=Email(
                to=user.email, username=user.username,
                context={'confirm_code': confirm_code.code}
            ),
            email_type=EmailType.confirm_email
        )
    except APIException as e:
        confirm_code.delete()
        raise e
