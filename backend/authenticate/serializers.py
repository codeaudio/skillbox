from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class ConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        max_length=90, min_length=8, required=True
    )
    confirm_code = serializers.CharField(
        max_length=32, min_length=32, required=True
    )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class AuthCodeSerializer(serializers.Serializer):
    auth_code = serializers.IntegerField(required=True)
    email = serializers.EmailField(required=True)

    @staticmethod
    def validate_code(value: int):
        if len(str(value)) != 10:
            raise serializers.ValidationError('code содержать 10 цифр')
        return value


class RefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=1000, min_length=20,
                                          required=True)
