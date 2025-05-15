from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.views.views import (TelegramAuthAPIView, UserProfileAPIView, CustomAuthTokenView)
from apps.account.views.connection_channels_views import (
	ChannelsUserAPIView,
	ChannelsUserCheckViews,
	ModifiedProfitPerTabView,
	UserProfileTypeDetailView
)

urlpatterns = [
	path('auth/telegram/', TelegramAuthAPIView.as_view(), name='telegram-login'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

	path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
	path('login/', CustomAuthTokenView.as_view(), name='custom-auth-token'),

	path('channels/', ChannelsUserAPIView.as_view(), name='channels-user'),
	path('channels/check/<str:channel_id>/', ChannelsUserCheckViews.as_view(), name='channels-user-check'),

	path('channels/modified_profit_per_tab/', ModifiedProfitPerTabView.as_view(), name='modified-profit-per-tab'),
	path('profile/type/<str:type>/', UserProfileTypeDetailView.as_view(), name='user-profile-type-detail'),
]

