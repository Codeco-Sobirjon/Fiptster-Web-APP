from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.views.views import (TelegramAuthAPIView, UserProfileAPIView, CustomAuthTokenView, UserProfileListView,
                                      UserCoinUpdatedView, ProfileSoundView, UserReferalsView, ReferalsPointsView)
from apps.account.views.connection_channels_views import (
	ChannelsUserAPIView,
	ChannelsUserCheckViews,
	ModifiedProfitPerTabView,
)

urlpatterns = [
	path('auth/telegram/', TelegramAuthAPIView.as_view(), name='telegram-login'),
	path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

	path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
	path('login/', CustomAuthTokenView.as_view(), name='custom-auth-token'),

	path('channels/', ChannelsUserAPIView.as_view(), name='channels-user'),
	path('channels/check/<str:channel_id>/', ChannelsUserCheckViews.as_view(), name='channels-user-check'),

	path('channels/modified_profit_per_tab/', ModifiedProfitPerTabView.as_view(), name='modified-profit-per-tab'),
	path('profile/grouped/', UserProfileListView.as_view(), name='user-profile-grouped'),

	path('profile/coin_updated/', UserCoinUpdatedView.as_view(), name='user-coin-updated'),
	path('profile/sound/', ProfileSoundView.as_view(), name='profile-sound'),

	path('profile/referals/', UserReferalsView.as_view(), name='user-referals'),
	path('profile/referals/points/', ReferalsPointsView.as_view(), name='referals-points'),
]

