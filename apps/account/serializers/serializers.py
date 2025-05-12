from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.account.models import CustomUser, UserProfile
from rest_framework.exceptions import AuthenticationFailed, ValidationError


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('uuid', 'profile_type', 'coin', 'coin_level', 'earn_per_tab', 'profit_per_hour', 'image')


class CustomUserSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'tg_id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'user_profile')

    def get_user_profile(self, obj):
        user_profile = get_object_or_404(UserProfile, user=obj)
        if user_profile:
            return UserProfileSerializer(user_profile, context={'request': self.context.get('request')}).data
        return None


class CustomAuthTokenSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'placeholder': 'Введите пароль'})

    class Meta:
        model = CustomUser
        fields = ('identifier', 'password')

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        if not identifier or not password:
            raise serializers.ValidationError("Телефон и пароль, оба поля обязательны")

        user_model = get_user_model()

        user = user_model.objects.filter(username=identifier).first()

        if user is None:
            raise AuthenticationFailed("Неверные данные, пользователь не найден")

        if not user.check_password(password):
            raise AuthenticationFailed("Неверные данные, неправильный пароль")

        return {
            'user': user,
        }

