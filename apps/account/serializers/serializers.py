from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.db.models import Window, F
from django.db.models.functions import DenseRank as DenseRankFunc
from rest_framework.exceptions import AuthenticationFailed

from apps.account.models import CustomUser, UserProfile, Referals, ReferalsPoints


class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('uuid', 'profile_type', 'coin', 'coin_level', 'earn_per_tab', 'profit_per_hour', 'image')


class CustomUserSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    user_rank = serializers.SerializerMethodField()
    profile_level = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'tg_id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'user_profile', 'user_rank',
                  'is_sound', 'profile_level')

    def get_user_profile(self, obj):
        user_profile = get_object_or_404(UserProfile, user=obj)
        if user_profile:
            return UserProfileSerializer(user_profile, context={'request': self.context.get('request')}).data
        return None

    def get_profile_level(self, obj):
        user_profile = UserProfile.objects.filter(user=obj).first()
        if not user_profile:
            return None

        profile_type = user_profile.profile_type
        type_order = [choice[0] for choice in UserProfile.UserProfileType.choices]

        try:
            return type_order.index(profile_type) + 1
        except ValueError:
            return None

    def get_user_rank(self, obj):
        user_profile = UserProfile.objects.filter(user=obj).first()
        if not user_profile:
            return None

        profile_type = user_profile.profile_type
        similar_profiles = UserProfile.objects.filter(profile_type=profile_type).order_by('-coin')
        user_ids = [profile.user.id for profile in similar_profiles]

        try:
            return user_ids.index(obj.id) + 1
        except ValueError:
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


class ProfileTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    coin_level = serializers.CharField()
    users_data = CustomUserSerializer(many=True)


class ProfileSoundSerializer(serializers.Serializer):
    sound = serializers.BooleanField(required=True)


class UserReferalsSerializer(serializers.ModelSerializer):
    invited_user = CustomUserSerializer()
    points = serializers.SerializerMethodField()

    class Meta:
        model = Referals
        fields = ('invited_user', 'points', 'created_at')

    def get_points(self, obj):
        referal_points = ReferalsPoints.objects.first()
        if referal_points:
            return referal_points.points
        return 0


class ReferalsPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferalsPoints
        fields = ('uuid', 'points', 'created_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['points'] = str(representation['points'])
        return representation
