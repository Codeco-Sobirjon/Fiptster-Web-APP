from django.contrib import admin

from apps.token_swap.models import TokenSwap


@admin.register(TokenSwap)
class TokenSwapAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'user', 'amount', 'total_exchange', 'created_at')
	list_filter = ('user',)
	search_fields = ['user__username']
	readonly_fields = ('uuid', 'created_at')

