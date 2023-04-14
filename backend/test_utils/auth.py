from rest_framework.test import APIClient

from authenticate.utils import gen_access_token


def client_auth(client: APIClient, username: str, email: str) -> None:
    """
    Parameters
    ----------
    client
        объект APIClient, который содержит метод credentials
    username
        юзернейм
    email
        почта
    """
    client.credentials(
        HTTP_AUTHORIZATION='Bearer ' + gen_access_token(
            username=username, email=email
        )
    )
