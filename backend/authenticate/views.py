from django.contrib.auth import authenticate, get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from authenticate.selectors import (get_user_by_auth_code_and_email,
                                    get_user_by_email)
from authenticate.serializers import (AuthCodeSerializer, ConfirmSerializer,
                                      LoginSerializer, RefreshSerializer)
from authenticate.services import (activate_auth_code, activate_confirm_code,
                                   add_token_to_black_list,
                                   check_token_in_black_list, send_auth_code)
from authenticate.utils import (decode_refresh_token, gen_access_token,
                                gen_refresh_token)

User = get_user_model()


@extend_schema(
    request=LoginSerializer, responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    user = get_user_by_email(email=email)
    send_auth_code(user=user)
    return Response(
        data={'detail': 'код отправлен на вашу почту'},
        status=200
    )


@extend_schema(
    request=ConfirmSerializer, responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def confirm(request):
    serializer = ConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    confirm_code = serializer.validated_data.get('confirm_code')
    email = serializer.validated_data.get('email')
    password = serializer.validated_data.get('password')
    user = authenticate(request, email=email, password=password)
    if not user:
        raise AuthenticationFailed('Некорректные данные')
    activate_confirm_code(confirm_code, user)
    return Response(
        data={'detail': 'Аккаунт успешно активирован'},
        status=200
    )


@extend_schema(
    request=AuthCodeSerializer, responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def token(request):
    serializer = AuthCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    auth_code = serializer.validated_data.get('auth_code')
    email = serializer.validated_data.get('email')
    user = get_user_by_auth_code_and_email(auth_code, email)
    activate_auth_code(code=auth_code, user=user)
    user_data = {
        'username': user.username, 'email': user.email
    }
    access_token = gen_access_token(**user_data)
    refresh_token = gen_refresh_token(**user_data)
    return Response(
        {'access_token': access_token, 'refresh_token': refresh_token},
        status=200
    )


@extend_schema(
    request=RefreshSerializer, responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def refresh(request):
    serializer = RefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh_token = serializer.validated_data.get('refresh_token')
    check_token_in_black_list(refresh_token)
    decoded_token = decode_refresh_token(refresh_token)
    username = decoded_token.get('username')
    email = decoded_token.get('email')
    user_data = {'username': username, 'email': email}
    add_token_to_black_list(refresh_token)
    access_token = gen_access_token(**user_data)
    refresh_token = gen_refresh_token(**user_data)
    return Response(
        {'access_token': access_token, 'refresh_token': refresh_token},
        status=200
    )


@extend_schema(
    request=RefreshSerializer, responses={200: None}, methods=('POST',)
)
@api_view(('POST',))
@authentication_classes([])
@permission_classes([])
def logout(request):
    serializer = RefreshSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    refresh_token = serializer.validated_data.get('refresh_token')
    add_token_to_black_list(refresh_token)
    return Response(status=200)
