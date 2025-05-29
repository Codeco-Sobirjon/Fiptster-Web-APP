from django.db import transaction
from kombu import uuid
from rest_framework import serializers

from apps.account.serializers.serializers import CustomUserSerializer
from apps.feeds.models import (
	FeedCategory,
	Feed,
	FeedLike,
	FeedComment,
	FeedCommentLike,
)


class FeedCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = FeedCategory
		fields = ('uuid', 'name', 'created_at')


class FeedSerializer(serializers.ModelSerializer):
	feed_category = FeedCategorySerializer(source='category', read_only=True)
	feed_comment_count = serializers.SerializerMethodField()
	feed_like_count = serializers.SerializerMethodField()
	comment_list = serializers.SerializerMethodField()

	class Meta:
		model = Feed
		fields = ('uuid', 'name', 'video_file', 'type', 'thumbnail', 'feed_category', 'description', 'feed_comment_count',
		          'feed_like_count', 'comment_list', 'created_at')

	def get_feed_comment_count(self, obj):
		return obj.comments.count()

	def get_feed_like_count(self, obj):
		return obj.likes.count()

	def get_comment_list(self, obj):
		return FeedCommentSerializer(obj.comments.all(), many=True, context={'request': self.context.get('request')}).data


class FeedLikeSerializer(serializers.ModelSerializer):
	user = CustomUserSerializer(read_only=True)

	class Meta:
		model = FeedLike
		fields = ('uuid', 'user', 'feed', 'created_at')


class FeedCommentSerializer(serializers.ModelSerializer):
	user = CustomUserSerializer(read_only=True)
	comment_like_count = serializers.SerializerMethodField()

	class Meta:
		model = FeedComment
		fields = ('uuid', 'user', 'feed', 'text', 'comment_like_count', 'created_at')

	def get_comment_like_count(self, obj):
		return obj.comment_likes.count()


class FeedDetailSerializer(serializers.ModelSerializer):
	feed_category = FeedCategorySerializer(source='category', read_only=True)
	feed_comment_count = serializers.SerializerMethodField()
	feed_like_count = serializers.SerializerMethodField()
	feed_like_list = serializers.SerializerMethodField()
	feed_comment_list = serializers.SerializerMethodField()

	class Meta:
		model = Feed
		fields = ('uuid', 'name', 'video_file', "send_feed", 'feeds_source', 'thumbnail', 'feed_category', 'description', 'feed_comment_count',
		          'feed_like_count', 'feed_like_list', 'feed_comment_list', 'created_at')

	def get_feed_comment_count(self, obj):
		return obj.comments.count()

	def get_feed_like_count(self, obj):
		return obj.likes.count()

	def get_feed_like_list(self, obj):
		return FeedLikeSerializer(obj.likes.all(), many=True, context={'request': self.context.get('request')}).data

	def get_feed_comment_list(self, obj):
		return FeedCommentSerializer(obj.comments.all(), many=True,
		                             context={'request': self.context.get('request')}).data


class FeedCommentListSerializer(serializers.ModelSerializer):
	class Meta:
		model = FeedComment
		fields = ('uuid', 'text', 'created_at')

	def create(self, validated_data):
		request = self.context.get('request')
		feed = self.context.get('feed')
		print(feed)
		user = request.user
		with transaction.atomic():
			return FeedComment.objects.create(user=user, feed=feed, **validated_data)


class FeedCommentLikeSerializer(serializers.ModelSerializer):
	class Meta:
		model = FeedCommentLike
		fields = ('uuid', 'created_at')

	def create(self, validated_data):
		request = self.context.get('request')
		feed_comment = self.context.get('comment')
		user = request.user
		with transaction.atomic():
			return FeedCommentLike.objects.create(user=user, feed_comment=feed_comment, **validated_data)


class FeedLikeListSerializer(serializers.ModelSerializer):
	class Meta:
		model = FeedLike
		fields = ('uuid', 'feed', 'created_at')

	def create(self, validated_data):
		request = self.context.get('request')
		user = request.user
		feed_id = self.context.get('feed')
		try:
			with transaction.atomic():
				if FeedLike.objects.filter(user=user, feed=feed_id).exists():
					raise serializers.ValidationError({'feed': 'Вы уже поставили лайк этой ленте'})
				return FeedLike.objects.create(user=user, feed=feed_id, **validated_data)
		except Feed.DoesNotExist:
			raise serializers.ValidationError({'feed': 'Лента с указанным UUID не найдена'})
