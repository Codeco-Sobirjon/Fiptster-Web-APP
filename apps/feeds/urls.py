from django.urls import path
from apps.feeds.views import (
	FeedCategoryListView,
	FeedListView,
	FeedDetailView,
	FeedCommentListView,
	FeedCommentLikeView,
	FeedLikeListView
)


urlpatterns = [
	path('categories/', FeedCategoryListView.as_view(), name='feed-category-list'),
	path('feeds/', FeedListView.as_view(), name='feed-list'),
	path('feeds/<uuid:uuid>/', FeedDetailView.as_view(), name='feed-detail'),

	path('feeds/comments/', FeedCommentListView.as_view(), name='feed-comment-list'),
	path('feeds/comments/like/', FeedCommentLikeView.as_view(), name='feed-comment-like'),

	path('feeds/likes/', FeedLikeListView.as_view(), name='feed-like-list'),
]
