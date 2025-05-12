from django_filters import rest_framework as filters

from apps.market.models import Market


class MarketFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.UUIDFilter(field_name='category__uuid')
    price_fiptp = filters.NumberFilter()

    class Meta:
        model = Market
        fields = ['name', 'category', 'price_fiptp']
