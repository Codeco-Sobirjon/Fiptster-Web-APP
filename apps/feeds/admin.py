from django.contrib import admin
from apps.feeds.models import (
	Feed, FeedCategory,
	FeedLike, FeedComment,
	FeedCommentLike
)


class FeedLikeInline(admin.TabularInline):
	model = FeedLike
	extra = 0
	readonly_fields = ('user', 'created_at')
	can_delete = False


class FeedCommentInline(admin.TabularInline):
	model = FeedComment
	extra = 0
	readonly_fields = ('user', 'text', 'created_at')
	can_delete = False
	show_change_link = True


class FeedCommentLikeInline(admin.TabularInline):
	model = FeedCommentLike
	extra = 0
	readonly_fields = ('user', 'created_at')
	can_delete = False


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name', 'category', 'type', 'created_at')
	list_filter = ('category', 'type')
	search_fields = ('name', 'description')
	inlines = [FeedLikeInline, FeedCommentInline]


@admin.register(FeedCategory)
class FeedCategoryAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'name', 'created_at')


@admin.register(FeedComment)
class FeedCommentAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'user', 'feed', 'text', 'created_at')
	inlines = [FeedCommentLikeInline]
	readonly_fields = ('user', 'feed', 'text', 'created_at')

	def has_module_permission(self, request):
		return False


admin.site.unregister(FeedLike) if admin.site.is_registered(FeedLike) else None
admin.site.unregister(FeedCommentLike) if admin.site.is_registered(FeedCommentLike) else None
