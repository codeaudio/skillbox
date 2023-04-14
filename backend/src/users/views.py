from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from users.permissions import UserPermission
from users.serializers import UserSerializer
from users.services import send_confirm

User = get_user_model()


class UserView(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (UserPermission,)
    lookup_field = 'username'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        send_confirm(user)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
