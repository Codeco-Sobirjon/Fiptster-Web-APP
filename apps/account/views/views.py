import json
import urllib

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import CustomUser, UserProfile
from apps.account.serializers.serializers import CustomUserSerializer, CustomAuthTokenSerializer
from apps.account.utils.telegram_auth import check_auth, TOKEN


class TelegramAuthAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Authenticate a user via Telegram and return JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['initData'],
            properties={
                'initData': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram authentication initData string'),
            },
        ),
        responses={
            200: openapi.Response(
                description='Successful authentication',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access_token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                    }
                ),
                examples={
                    'application/json': {
                        'access_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'refresh_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            ),
        }
    )
    def post(self, request):
        init_data_str = request.data.get("initData", "")
        if not init_data_str:
            return Response({'error': 'initData — обязательное поле.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            parsed = urllib.parse.parse_qs(init_data_str)
            processed_data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in parsed.items()}
            user_json = processed_data.get("user")
            if not user_json:
                return Response({'error': 'Нет информации о пользователе'}, status=status.HTTP_400_BAD_REQUEST)
            user_data = json.loads(user_json)
            if not check_auth(processed_data, TOKEN):
                return Response({'error': 'Неправильная аутентификация Telegram'}, status=status.HTTP_403_FORBIDDEN)
            telegram_id = user_data.get("id")
            if not telegram_id:
                return Response({'error': 'Требуется идентификатор Telegram'}, status=status.HTTP_400_BAD_REQUEST)
            username = user_data.get("username", f"tg_{telegram_id}")
            first_name = user_data.get("first_name", "")
            last_name = user_data.get("last_name", "")
            image_url = user_data.get("photo_url", "")
            user = CustomUser.objects.filter(tg_id=telegram_id).first()
            user, created = CustomUser.objects.update_or_create(
                tg_id=telegram_id,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'avatar': image_url,
                }
            )
            if created:
                UserProfile.objects.create(user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            return Response({'error': 'Неверный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Ошибка сервера: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Retrieve the profile of the authenticated user",
        responses={
            200: openapi.Response(
                description='User profile retrieved successfully',
                schema=CustomUserSerializer,
                examples={
                    'application/json': {
                        'uuid': '12345678-1234-5678-1234-567812345678',
                        'username': 'tg_123456',
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'tg_id': '123456',
                        'avatar': 'https://example.com/avatar.jpg'
                    }
                }
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomAuthTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Authenticate a user and return JWT tokens",
        request_body=CustomAuthTokenSerializer,
        responses={
            200: openapi.Response(
                description='Successful authentication',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                    }
                ),
                examples={
                    'application/json': {
                        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                        'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
                    }
                }
            ),
        }
    )
    def post(self, request):
        serializer = CustomAuthTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

