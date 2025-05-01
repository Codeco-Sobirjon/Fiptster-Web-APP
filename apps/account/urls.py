from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.views import ( TelegramAuthAPIView, UserProfileAPIView )

urlpatterns = [
	path('auth/telegram/', TelegramAuthAPIView.as_view(), name='telegram-login'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

	path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
]

