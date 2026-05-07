from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя (чтение)"""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "name",
            "avatar",
            "country",
            "phone_number",
            "comment",
            "date_joined",
            "telegram_chat_id",
        ]
        read_only_fields = ["id", "date_joined", "telegram_chat_id"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ["email", "name", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Сериализатор для входа"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления профиля"""

    class Meta:
        model = CustomUser
        fields = ["name", "avatar", "country", "phone_number", "comment"]


class TelegramSetSerializer(serializers.Serializer):
    """Сериализатор для привязки Telegram"""

    telegram_chat_id = serializers.CharField(required=True)
