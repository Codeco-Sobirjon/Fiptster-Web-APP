from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
		responses={
			200: openapi.Response(
				description="Успешное создание комментария к ленте",
				schema=FeedCommentListSerializer()
			)
		}
	)
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedCommentLikeView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedCommentLikeSerializer

	@swagger_auto_schema(
		tags=["Feeds Comments Likes"],
		request_body=FeedCommentLikeSerializer,
		responses={
			200: openapi.Response(
				description="Успешное добавление лайка к комментарию",
				schema=FeedCommentLikeSerializer()
			)
		}
	)
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FeedLikeListView(APIView):
	permission_classes = [IsAuthenticated]
	serializer_class = FeedLikeListSerializer

	@swagger_auto_schema(
		tags=["Feeds Likes"],
		request_body=FeedLikeListSerializer,
		responses={
			200: openapi.Response(
				description="Успешное добавление лайка к ленте",
				schema=FeedLikeListSerializer()
			)
		}
	)
	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)