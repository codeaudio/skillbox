from django.urls import path

from authenticate.views import confirm, login, refresh, token

urlpatterns = [
    path(
        'login', login,
        name='login'
    ),
    path(
        'token', token,
        name='token'
    ),
    path(
        'confirm', confirm,
        name='confirm'
    ),
    path(
        'refresh', refresh,
        name='refresh'
    ),
]
