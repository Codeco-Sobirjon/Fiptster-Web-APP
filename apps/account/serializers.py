from rest_framework import serializers
from apps.account.models import CustomUser, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = ('id', 'profile_type', 'coin', 'coin_level', 'earn_per_tab', 'profit_per_hour', 'image')
		read_only_fields = ('id',)


class CustomUserSerializer(serializers.ModelSerializer):
	user_profile = serializers.SerializerMethodField()

	class Meta:
		model = CustomUser
		fields = ('id', 'tg_id', 'username', 'first_name', 'last_name', 'email', 'avatar', 'user_profile')
		read_only_fields = ('id',)

	def get_user_profile(self, obj):
		user_profile = obj.profile
		if user_profile:
			return UserProfileSerializer(user_profile, context={'request': self.context.get('request')}).data
		return None
