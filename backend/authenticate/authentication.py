from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from authenticate.utils import decode_access_token


class JWTAuth(BaseAuthentication):
    keyword = 'Bearer'
    model = get_user_model()

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return AnonymousUser(), None
        if self.keyword not in auth_header:
            raise exceptions.AuthenticationFailed
        access_token = auth_header.replace('Bearer ', '')
        payload = decode_access_token(access_token)
        try:
            user = self.model.objects.get(email=payload.get('email'))
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Пользователь отсутсвует')
        return user, None
