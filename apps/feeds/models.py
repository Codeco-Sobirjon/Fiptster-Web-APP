import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FeedCategory(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Название')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Категория'
		verbose_name_plural = 'Категории'

	def __str__(self):
		return self.name


class Feed(models.Model):

	class VideoType(models.TextChoices):
		REELS = 'reels', 'Reels'
		ADVERTISEMENT = 'advertisement', 'Advertisement'

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	name = models.CharField(max_length=255, verbose_name='Название', null=True, blank=True)
	description = models.TextField(verbose_name='Описание', null=True, blank=True)
	video_file = models.FileField(upload_to='videos/', verbose_name='Видео файл', null=True, blank=True)
	thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, verbose_name='Миниатюра')
	type = models.CharField(max_length=255, choices=VideoType.choices, default=VideoType.REELS, verbose_name='Тип')
	category = models.ForeignKey(FeedCategory, on_delete=models.CASCADE, related_name='feeds', verbose_name='Категория')
	send_feed = models.IntegerField(default=0, verbose_name='Отправить ленту')
	feeds_source = models.URLField(max_length=255, null=True, blank=True, verbose_name='Источник ленты')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Лента'
		verbose_name_plural = 'Ленты'

	def __str__(self):
		return self.name


class FeedLike(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_likes', verbose_name='Пользователь')
	feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='likes', verbose_name='Лента')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Лайк'
		verbose_name_plural = 'Лайки'

	def __str__(self):
		return f"{self.user.username} - {self.feed.name}"


class FeedComment(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_comments', verbose_name='Пользователь')
	feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='comments', verbose_name='Лента')
	text = models.TextField(verbose_name='Текст')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Комментарии'
		verbose_name_plural = 'Комментарии'

	def __str__(self):
		return f"{self.user.username} - {self.feed.name}"


class FeedCommentLike(models.Model):
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='UUID')
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_comment_likes', verbose_name='Пользователь')
	feed_comment = models.ForeignKey(FeedComment, on_delete=models.CASCADE, related_name='likes', verbose_name='Комментарии')
	created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

	objects = models.Manager()

	class Meta:
		verbose_name = 'Лайк'
		verbose_name_plural = 'Лайки'

	def __str__(self):
		return f"{self.user.username} - {self.feed_comment.text}"
