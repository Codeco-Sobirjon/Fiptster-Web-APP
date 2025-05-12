from rest_framework import serializers

from apps.market.models import Category, Market, Order


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ('uuid', 'name', 'created_at')


class MarketSerializer(serializers.ModelSerializer):
	class Meta:
		model = Market
		fields = ['uuid', 'name', 'price_fiptp', 'price_dollor', 'image', 'sizes', 'category', 'created_at']

	def to_representation(self, instance):
		data = super().to_representation(instance)
		data['category'] = CategorySerializer(instance.category).data
		return data


class MarketDetailSerializer(serializers.ModelSerializer):
	class Meta:
		model = Market
		fields = ['uuid', 'name', 'price_fiptp', 'price_dollor', 'image', 'sizes', 'category', 'created_at']
		read_only_fields = ['uuid', 'created_at']
