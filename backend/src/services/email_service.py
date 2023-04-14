import logging
from abc import ABC, abstractmethod
from enum import Enum

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.exceptions import APIException

from services.dto import Email


class EmailType(Enum):
    auth_code = 'auth_code'
    confirm_email = 'confirm_email'


class AbstractEmail(ABC):
    @abstractmethod
    def prepare_html_data(self) -> dict:
        pass


class ConfirmEmail(AbstractEmail):
    __slots__ = ('email_data',)

    def __init__(self, email_data: Email):
        self.email_data = email_data

    def prepare_html_data(self) -> dict:
        return {
            'subject': 'Код доступа',
            'to': self.email_data.to,
            'action': 'Код доступа',
            'html_message': render_to_string(
                'email/confirm_code.html', {
                    'confirm_code':
                        self.email_data.context.get('confirm_code'),
                    'username': self.email_data.username,
                })
        }


class EmailAuthCode(AbstractEmail):
    __slots__ = ('email_data',)

    def __init__(self, email_data: Email):
        self.email_data = email_data

    def prepare_html_data(self) -> dict:
        return {
            'subject': 'Код доступа',
            'to': self.email_data.to,
            'action': 'Код доступа',
            'html_message': render_to_string(
                'email/auth_code.html', {
                    'auth_code': self.email_data.context.get('auth_code'),
                    'username': self.email_data.username,
                    'exp': 60
                })
        }


email_type_to_data = {
    EmailType.auth_code: EmailAuthCode,
    EmailType.confirm_email: ConfirmEmail
}


def send_email(email_data: Email, email_type: EmailType) -> None:
    """

    Parameters
    ----------
    email_data :
        Email dataclass
    email_type :
        email_type enum type

    Raises
    -------
    APIException
    """
    prepared_html_data = email_type_to_data.get(
        email_type
    )(email_data).prepare_html_data()
    html_message = prepared_html_data.get('html_message')
    plain_message = strip_tags(html_message)
    to = prepared_html_data.get('to')
    to = [to] if isinstance(to, str) else [*to]
    is_sent = send_mail(
        prepared_html_data.get('subject'),
        plain_message,
        settings.EMAIL_HOST_USER,
        to,
        html_message=html_message,
        fail_silently=True,
    )
    if not is_sent:
        logging.error(f'Письо не отправлено {prepared_html_data}')
        raise APIException('Письмо не было отправлено')
    logging.info(f'Письо успешно отправлено {prepared_html_data}')
