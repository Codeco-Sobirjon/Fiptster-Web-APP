import django_filters

from apps.feeds.models import Feed


class FeedFilter(django_filters.FilterSet):
    category = django_filters.UUIDFilter(field_name='category__uuid')

    class Meta:
        model = Feed
        fields = ['category']
