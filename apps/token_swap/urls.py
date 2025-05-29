from django.urls import path

from apps.token_swap.views import TokenSwapView

urlpatterns = [
	path('token-swap/', TokenSwapView.as_view(), name='token-swap'),
]