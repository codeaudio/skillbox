import datetime

from users.models import AuthCode


def expire_auth_code_control(func):
    """Декоратор для удаления истекших кодов для логина"""
    def wrapper(*args, **kwargs):
        auth_codes = AuthCode.objects.filter(
            exp__lte=datetime.datetime.now().date()
        )
        if auth_codes.exists():
            auth_codes.delete()
        return func(*args, **kwargs)

    return wrapper
