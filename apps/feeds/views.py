from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from kombu import uuid
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.feeds.filters import FeedFilter
from apps.feeds.models import (
	FeedCategory,
	Feed,
	FeedLike,
	FeedComment,
	FeedCommentLike,
)
from apps.feeds.serializers import (
	FeedCategorySerializer,
	FeedSerializer,
	FeedDetailSerializer,
	FeedCommentListSerializer,
	FeedCommentLikeSerializer,
	FeedLikeListSerializer,
)


class FeedCategoryListView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedCategorySerializer

	@swagger_auto_schema(
		tags=["Feeds Categories"],
		responses={
			200: openapi.Response(
				description="Список категорий",
				schema=FeedCategorySerializer(many=True),
			)
		}
	)
	def get(self, request):
		categories = FeedCategory.objects.all()
		serializer = self.serializer_class(categories, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)


class FeedListView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedSerializer
	filter_backends = [DjangoFilterBackend]
	filterset_class = FeedFilter

	@swagger_auto_schema(
		tags=["Feeds"],
		manual_parameters=[
			openapi.Parameter(
				'category_uuid',
				openapi.IN_QUERY,
				description="Filter by category UUID",
				type=openapi.FORMAT_UUID
			),
		],
		responses={
			200: openapi.Response(
				description="Список постов",
				schema=FeedSerializer(many=True),
			)
		}
	)
	def get(self, request):
		feeds = Feed.objects.all()

		filterset = self.filterset_class(request.query_params, queryset=feeds)
		if not filterset.is_valid():
			return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

		filtered_feeds = filterset.qs

		reels_feeds = filtered_feeds.filter(type=Feed.VideoType.REELS).order_by('?')[:20]

		advertisement_feeds = filtered_feeds.filter(type=Feed.VideoType.ADVERTISEMENT).order_by('?')[:4]

		result_feeds = []
		reels_iterator = iter(reels_feeds)
		ad_iterator = iter(advertisement_feeds)

		for i in range(1, 25):
			if i in [5, 10, 15, 20]:
				try:
					result_feeds.append(next(ad_iterator))
				except StopIteration:
					pass
			else:
				try:
					result_feeds.append(next(reels_iterator))
				except StopIteration:
					pass

		serializer = self.serializer_class(result_feeds, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class FeedDetailView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedDetailSerializer

	@swagger_auto_schema(
		tags=["Feeds"],
		operation_description="Получение поста по UUID",
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID поста",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Пост",
				schema=FeedDetailSerializer(),
			)
		}
	)
	def get(self, request, uuid):
		try:
			feed = Feed.objects.get(uuid=uuid)
			feed.send_feed += 1
			feed.save()
		except ObjectDoesNotExist:
			return Response({"error": "Feed not found"}, status=status.HTTP_404_NOT_FOUND)
		serializer = self.serializer_class(feed, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class FeedCommentListView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedCommentListSerializer

	@swagger_auto_schema(
		tags=["Feeds Comments"],
		request_body=FeedCommentListSerializer,
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID поста, к которому добавляется комментарий",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Успешное создание комментария к ленте",
				schema=FeedCommentListSerializer()
			)
		}
	)
	def post(self, request, *args, **kwargs):
		feed_uuid = kwargs.get('uuid')
		feed = get_object_or_404(Feed, uuid=feed_uuid)
		serializer = self.serializer_class(data=request.data, context={'request': request, 'feed': feed})
		if serializer.is_valid():
			serializer.save()
			return Response({"message": "Comment added successfully"}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedCommentLikeView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedCommentLikeSerializer

	@swagger_auto_schema(
		tags=["Feeds Comments Likes"],
		request_body=FeedCommentLikeSerializer,
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID комментария, к которому добавляется лайк",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Успешное добавление лайка к комментарию",
				schema=FeedCommentLikeSerializer()
			)
		}
	)
	def post(self, request, *args, **kwargs):
		feed_comment_uuid = kwargs.get('uuid')
		comment = get_object_or_404(FeedComment, uuid=feed_comment_uuid)
		serializer = self.serializer_class(data=request.data, context={'request': request, 'comment': comment})
		if serializer.is_valid():
			serializer.save()
			return Response({"message": "Like added successfully"}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedCommentDisLikeView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		tags=["Feeds Comments Likes"],
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID комментария",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Успешное удаление лайка к комментарию",
				schema=FeedCommentLikeSerializer()
			)
		}
	)
	def delete(self, request, *args, **kwargs):
		try:
			comment = get_object_or_404(FeedComment, uuid=kwargs['uuid'])
			comment_like = FeedCommentLike.objects.get(feed_comment=comment, user=request.user)
			comment_like.delete()
			return Response({"message": "Like removed successfully"}, status=status.HTTP_200_OK)
		except ObjectDoesNotExist:
			return Response({"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND)


class FeedLikeListView(APIView):
	permission_classes = [IsAuthenticated]
	@swagger_auto_schema(
		tags=["Feeds Likes"],
		manual_parameters=[
			openapi.Parameter(
				'feed',
				openapi.IN_PATH,
				description="UUID поста",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Успешное добавление лайка к ленте"
			)
		}
	)

	def get(self, request, *args, **kwargs):
		feed = get_object_or_404(Feed, uuid=kwargs.get('uuid'))
		FeedLike.objects.get_or_create(user=request.user, feed=feed)
		return Response({"message": "Like added successfully"}, status=status.HTTP_200_OK)


class FeedDisLikeView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		tags=["Feeds Likes"],
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID поста",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		],
		responses={
			200: openapi.Response(
				description="Успешное удаление лайка к ленте"
			)
		}
	)
	def delete(self, request, *args, **kwargs):
		try:
			feed_like = FeedLike.objects.get(feed__uuid=kwargs['uuid'], user=request.user)
			feed_like.delete()
			return Response({"message": "Like removed successfully"}, status=status.HTTP_200_OK)
		except ObjectDoesNotExist:
			return Response({"error": "Like not found"}, status=status.HTTP_404_NOT_FOUND)
