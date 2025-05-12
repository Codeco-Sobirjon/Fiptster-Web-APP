from django.contrib import admin

from apps.market.models import (
	Category,
	Market,
	Order,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name')


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name', 'price_fiptp', 'price_dollor', 'image', 'sizes', 'category')
	list_filter = ('category',)
	search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'user', 'market', 'sizes', 'full_name', 'email', 'address')
	list_filter = ('user',)
	search_fields = ('user__username', 'market__name', 'full_name', 'email', 'address')
