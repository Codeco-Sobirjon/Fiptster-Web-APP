from django.urls import path
from apps.market.views import CategoryAPIView, MarketAPIView, MarketDetailAPIView, CreateOrderView

urlpatterns = [
	path('categories/', CategoryAPIView.as_view(), name='category-list'),
	path('markets/', MarketAPIView.as_view(), name='market-list'),
	path('markets/<uuid:uuid>/', MarketDetailAPIView.as_view(), name='market-detail'),

	path('orders/create/', CreateOrderView.as_view(), name='create-order'),

]
