from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404

from authenticate.decorators import expire_auth_code_control
from users.models import AuthCode

User = get_user_model()


@expire_auth_code_control
def get_user_by_auth_code_and_email(code: int, email: str) -> User:
    """
    Parameters
    ----------
    code :
        код для модели AuthCode
    email :
        почта пользователя
    Returns
    -------
    User :
        объект модели пользователя
    Raises
    ----------
    NotFound
    """
    auth_code = AuthCode.objects.filter(code=code, user__email=email)
    if not auth_code.exists():
        raise NotFound('Код доступа не найден')
    return auth_code.first().user


def get_user_by_email(email: str) -> User:
    """
    Parameters
    ----------
    email :
        почта пользователя
    Returns
    -------
    User :
        объект модели пользователя
    """
    return get_object_or_404(User, email=email)
