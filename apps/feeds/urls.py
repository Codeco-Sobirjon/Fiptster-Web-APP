from django.urls import path
from apps.feeds.views import (
	FeedCategoryListView,
	FeedListView,
	FeedDetailView,
	FeedCommentListView,
	FeedCommentLikeView,
	FeedCommentDisLikeView,
	FeedLikeListView,
	FeedDisLikeView
)


urlpatterns = [
	path('categories/', FeedCategoryListView.as_view(), name='feed-category-list'),
	path('feeds/', FeedListView.as_view(), name='feed-list'),
	path('feeds/<uuid:uuid>/', FeedDetailView.as_view(), name='feed-detail'),

	path('feeds/comments/<uuid:uuid>/', FeedCommentListView.as_view(), name='feed-comment-list'),
	path('feeds/comments/like/<uuid:uuid>/', FeedCommentLikeView.as_view(), name='feed-comment-like'),
	path('feeds/comments/dislike/<uuid:uuid>/', FeedCommentDisLikeView.as_view(), name='feed-comment-dislike'),

	path('feeds/likes/<uuid:uuid>/', FeedLikeListView.as_view(), name='feed-like-list'),
	path('feeds/dislike/<uuid:uuid>/', FeedDisLikeView.as_view(), name='feed-dislike'),
]
