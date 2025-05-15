import django_filters

from apps.feeds.models import Feed


class FeedFilter(django_filters.FilterSet):
    category_uuid = django_filters.UUIDFilter(field_name='category_uuid')

    class Meta:
        model = Feed
        fields = ['category_uuid']
