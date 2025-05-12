import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.market.filters import MarketFilter
from apps.market.models import Market, Order, Category
from apps.market.pagination import CustomPagination
from apps.market.serializers import CategorySerializer, MarketSerializer, MarketDetailSerializer


class CategoryAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		tags=['Market'],
		responses={
			200: CategorySerializer(many=True),
		}
	)
	def get(self, request):
		categories = Category.objects.all()
		serializer = CategorySerializer(categories, many=True, context={'request': request})
		return Response(serializer.data, status=status.HTTP_200_OK)


class MarketAPIView(APIView):
	permission_classes = [IsAuthenticated]
	filter_backends = [DjangoFilterBackend]
	filterset_class = MarketFilter
	pagination_class = CustomPagination

	@swagger_auto_schema(
		tags=['Market'],
		responses={
			200: MarketSerializer(many=True),
		},
		manual_parameters=[
			openapi.Parameter('name', openapi.IN_QUERY, description="Filter by market name (case-insensitive)",
			                  type=openapi.TYPE_STRING),
			openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category UUID", type=openapi.TYPE_STRING),
			openapi.Parameter('price_fiptp', openapi.IN_QUERY, description="Filter by price_fiptp",
			                  type=openapi.TYPE_NUMBER),
			openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
			openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page",
			                  type=openapi.TYPE_INTEGER),
		]
	)
	def get(self, request):
		markets = Market.objects.all()

		filterset = MarketFilter(request.query_params, queryset=markets)

		if not filterset.is_valid():
			return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

		filtered_markets = filterset.qs

		paginator = CustomPagination()
		paginated_markets = paginator.paginate_queryset(filtered_markets, request)
		serializer = MarketSerializer(paginated_markets, many=True, context={'request': request})

		return paginator.get_paginated_response(serializer.data)


class MarketDetailAPIView(APIView):
	permission_classes = [IsAuthenticated]

	@swagger_auto_schema(
		tags=['Market'],
		operation_description="Retrieve details of a specific market item by UUID",
		responses={
			200: MarketDetailSerializer(),
			404: openapi.Response(description="Market item not found"),
		},
		manual_parameters=[
			openapi.Parameter(
				'uuid',
				openapi.IN_PATH,
				description="UUID of the market item",
				type=openapi.TYPE_STRING,
				format='uuid',
				required=True
			),
		]
	)
	def get(self, request, *args, **kwargs):
		try:
			market = get_object_or_404(Market, uuid=kwargs.get('uuid'))
			serializer = MarketDetailSerializer(market, context={'request': request})
			return Response(serializer.data, status=status.HTTP_200_OK)
		except ValueError:
			return Response({"error": "Invalid UUID format"}, status=status.HTTP_400_BAD_REQUEST)
