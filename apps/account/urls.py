from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.views import ( TelegramLoginView )

urlpatterns = [
	path('auth/telegram/', TelegramLoginView.as_view(), name='telegram-login'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]

