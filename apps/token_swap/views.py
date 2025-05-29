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

from apps.token_swap.models import TokenSwap
from apps.token_swap.serializers import TokenSwapSerializer


class TokenSwapView(APIView):
	permission_classes = (IsAuthenticated,)

	@swagger_auto_schema(
		request_body=TokenSwapSerializer,
		tags=["Token Swap"],
		responses={
			201: openapi.Response(
				description="Token swap created successfully",
				schema=TokenSwapSerializer
			),
			400: openapi.Response(
				description="Bad request",
				schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
					'detail': openapi.Schema(type=openapi.TYPE_STRING)
				})
			)
		}
	)
	def post(self, request, *args, **kwargs):
		serializer = TokenSwapSerializer(data=request.data, context={'request': request})
		if serializer.is_valid():
			token_swap = serializer.save()
			return Response(TokenSwapSerializer(token_swap).data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
