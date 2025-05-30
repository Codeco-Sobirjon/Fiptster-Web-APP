from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.account.serializers.connection_channels_serializers import (
	ChannelsUserSerializer,
	GroupedByTaskTypeSerializer,
	ChannelsUserGroupedSerializer,
)
from apps.account.models import ChannelsUser, ConnectToChannel, UserProfile, CustomUser


class ChannelsUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Channels'],
        responses={
            200: ChannelsUserGroupedSerializer(many=True),
        }
    )
    def get(self, request):
        channels = ChannelsUser.objects.all()
        serializer = ChannelsUserGroupedSerializer(channels, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChannelsUserCheckViews(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Channels'],
        manual_parameters=[
            openapi.Parameter(
                'secret_code',
                openapi.IN_QUERY,
                description="Secret code for verifying YouTube channel (required only for YouTube)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(description="Successfully connected"),
            400: openapi.Response(description="Invalid secret code or missing channel ID"),
            404: openapi.Response(description="Channel not found")
        }
    )
    def get(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        if not channel_id:
            return Response({"error": "Channel ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            channel = ChannelsUser.objects.get(uuid=channel_id)

            if channel.channel_type == ChannelsUser.ChannelType.first_choice:
                secret_code = request.GET.get('secret_code')
                if channel.secret_code != secret_code:
                    return Response({"msg": "Invalid secret code"}, status=status.HTTP_400_BAD_REQUEST)

            connection, created = ConnectToChannel.objects.get_or_create(user=request.user, channel=channel)

            if created:
                try:
                    user_profile = UserProfile.objects.get(user=request.user)
                    user_profile.coin += int(channel.channel_coin)
                    user_profile.save()
                except ObjectDoesNotExist:
                    return Response({"msg": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
                return Response({"msg": "Successfully connected"}, status=status.HTTP_200_OK)
            else:
                return Response({"msg": "Already connected"}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"exists": False}, status=status.HTTP_404_NOT_FOUND)


class ModifiedProfitPerTabView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_summary="Increment user's profit_per_hour",
        operation_description="This endpoint increments the authenticated user's "
                              "`profit_per_hour` by 1 and saves the updated value.",
        responses={
            200: openapi.Response(
                description="Successfully modified",
                examples={
                    "application/json": {
                        "msg": "Successfully modified"
                    }
                }
            ),
            401: openapi.Response(description="Authentication credentials were not provided or invalid"),
            404: openapi.Response(description="User profile not found")
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        profile_profit_per_hour_increment = UserProfile.objects.select_related('user').filter(user=user).first()
        profile_profit_per_hour_increment.profit_per_hour += 1
        profile_profit_per_hour_increment.save()
        return Response({"msg": "Successfully modified"}, status=status.HTTP_200_OK)

