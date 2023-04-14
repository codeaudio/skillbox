import datetime
import random

from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError, transaction
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404

from authenticate.decorators import expire_auth_code_control
from services.dto import Email
from services.email_service import EmailType, send_email
from users.models import AuthCode, ConfirmCode, User


def generate_auth_code() -> int:
    """
    Returns
    -------
    random_int :
        рандомное 8 значное число
    """
    return random.randint(1000000000, 9999999999)


@expire_auth_code_control
def create_auth_code(user: User) -> AuthCode:
    """
    Parameters
    ----------
    user :
        объект модели AuthCode
    Returns
    -------
    AuthCode :
        объект модели AuthCode
    Raises
    -------
    APIException
    """
    try:
        return AuthCode.objects.create(
            code=generate_auth_code(),
            user=user,
            exp=datetime.datetime.now() + settings.AUTH_CODE_EXP
        )
    except IntegrityError:
        raise APIException(detail='Код уже был создан')


def send_auth_code(user: User) -> None:
    """
    Parameters
    ----------
    user :
        объект модели User
    Raises
    ----------
    APIException
    """
    if not user.is_active:
        raise APIException('Активируйте аккаунт')
    auth_code = create_auth_code(user)
    try:
        send_email(
            email_data=Email(
                to=user.email, username=user.username,
                context={'auth_code': auth_code.code}
            ),
            email_type=EmailType.auth_code
        )
    except APIException as e:
        auth_code.delete()
        raise e


def activate_auth_code(code: int, user: User) -> None:
    """
    Parameters
    ----------
    code :
        int код для модели AuthCode
    user :
        объект модели User

    """
    AuthCode.objects.filter(code=code, user=user).delete()


@transaction.atomic
def activate_confirm_code(code: str, user: User) -> None:
    """
    Parameters
    ----------
    code :
        int код для модели ConfirmCode
    user :
        объект модели User
    """
    instance = get_object_or_404(ConfirmCode, code=code, user_id=user)
    user = instance.user
    instance.delete()
    user.is_confirm = True
    user.save()


def add_token_to_black_list(token: str):
    """
    Parameters
    ----------
    token :
        токен
    """
    cache.set(token, False, timeout=settings.REFRESH_TOKEN_EXP.total_seconds())


def check_token_in_black_list(token: str):
    """
    Parameters
    ----------
    token :
        токен
    Raises
    ----------
    APIException
    """
    if cache.get(token) is False:
        raise APIException('refresh_token в черном списке')
