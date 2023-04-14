import datetime

import jwt
from django.conf import settings
from rest_framework import exceptions


def decode_token(token: str) -> dict:
    """
    Parameters
    ----------
    token :
        токен
    Returns
    -------
    payload :
        полезная нагрузка
    Raises
    -------
    AuthenticationFailed
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms='HS256'
        )
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            detail='token expired'
        )
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed(
            detail='invalid token'
        )
    return payload


def decode_access_token(token: str) -> dict:
    """
    Parameters
    ----------
    token :
        аксес токен
    Returns
    -------
    payload :
        полезная нагрузка
    Raises
    -------
    AuthenticationFailed
    """
    payload = decode_token(token)
    if payload.get('type') != 'access':
        raise exceptions.AuthenticationFailed(
            detail='invalid token'
        )
    return payload


def decode_refresh_token(token: str) -> dict:
    """
    Parameters
    ----------
    token :
        аксес токен

    Returns
    -------
    payload :
        полезная нагрузка
    Raises
    -------
    AuthenticationFailed
    """
    payload = decode_token(token)
    if payload.get('type') != 'refresh':
        raise exceptions.AuthenticationFailed(
            detail='invalid token'
        )
    return payload


def gen_access_token(username: str, email: str) -> str:
    """
    Parameters
    ----------
    username :
        имя пользователя
    email :
        почта пользователя
    Returns
    -------
    access_token :
        аксес токен
    """
    access_payload = {
        'exp': datetime.datetime.utcnow() + settings.ACCESS_TOKEN_EXP,
        'iat': datetime.datetime.utcnow(),
        'username': username,
        'email': email,
        'type': 'access'
    }
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    return access_token


def gen_refresh_token(username: str, email: str) -> str:
    """
    Parameters
    ----------
    username :
        имя пользователя
    email :
        почта пользователя
    Returns
    -------
    access_token :
        рефреш токен
    """
    refresh_payload = {
        'exp': datetime.datetime.utcnow() + settings.REFRESH_TOKEN_EXP,
        'iat': datetime.datetime.utcnow(),
        'username': username,
        'email': email,
        'type': 'refresh'
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm='HS256'
    )
    return refresh_token
