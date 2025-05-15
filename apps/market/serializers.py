from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
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


class CreateOrderSerializer(serializers.ModelSerializer):
	sizes = serializers.MultipleChoiceField(choices=Order.SizeType.choices)
	market = serializers.UUIDField()

	class Meta:
		model = Order
		fields = [
			'uuid', 'user', 'market', 'sizes',
			'full_name', 'email', 'address', 'city', 'country',
			'zip_code', 'is_shipping', 'created_at'
		]
		read_only_fields = ['uuid', 'created_at']

	def create(self, validated_data):
		request = self.context.get('request')
		user = request.user

		with transaction.atomic():
			order = Order.objects.create(user=user, **validated_data)
		return order
