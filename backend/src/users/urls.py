from django.urls import path

from users.views import UserView

urlpatterns = [
    path(
        'registration', UserView.as_view({'post': 'create'}),
        name='user_registration'
    ),
    path(
        '', UserView.as_view({'get': 'list'}),
        name='users'
    ),
    path(
        '<str:username>', UserView.as_view({'get': 'retrieve'}),
        name='user'
    ),
]
