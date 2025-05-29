import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FeedCategory(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Name')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = '1. Category'
		verbose_name_plural = '1. Categories'

	def __str__(self):
		return self.name


class Feed(models.Model):
	class VideoType(models.TextChoices):
		REELS = 'reels', 'Reels'
		ADVERTISEMENT = 'advertisement', 'Advertisement'

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Name', null=True, blank=True)
	description = models.TextField(verbose_name='Description', null=True, blank=True)
	video_file = models.FileField(upload_to='videos/', verbose_name='Video File', null=True, blank=True)
	thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, verbose_name='Thumbnail')
	type = models.CharField(max_length=255, choices=VideoType.choices, default=VideoType.REELS, verbose_name='Type')
	category = models.ForeignKey(FeedCategory, on_delete=models.CASCADE, related_name='feeds', verbose_name='Category')
	send_feed = models.IntegerField(default=0, verbose_name='Send Feed')
	feeds_source = models.URLField(max_length=255, null=True, blank=True, verbose_name='Feed Source')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = '2. Feed'
		verbose_name_plural = '2. Feeds'

	def __str__(self):
		return self.name


class FeedLike(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_likes', verbose_name='User',
	                         null=True, blank=True)
	feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='likes', verbose_name='Feed',
	                         null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Like'
		verbose_name_plural = 'Likes'

	def __str__(self):
		return f"{self.user.username} - {self.feed.name}"


class FeedComment(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_comments', verbose_name='User',
	                         null=True, blank=True)
	feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='comments', verbose_name='Feed',
	                         null=True, blank=True)
	text = models.TextField(verbose_name='Text')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Comment'
		verbose_name_plural = 'Comments'

	def __str__(self):
		return f"{self.user.username} - {self.feed.name}"


class FeedCommentLike(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_comment_likes', verbose_name='User',
	                         null=True, blank=True)
	feed_comment = models.ForeignKey(FeedComment, on_delete=models.CASCADE, related_name='comment_likes',
	                                 verbose_name='Comment',
	                                 null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Comment Like'
		verbose_name_plural = 'Comment Likes'

	def __str__(self):
		return f"{self.user.username}"
