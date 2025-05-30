import json
import os
import urllib
import uuid
from collections import defaultdict
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import get_object_or_404

from django.core.files.base import ContentFile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import CustomUser, UserProfile, Referals, ReferalsPoints
from apps.account.serializers.serializers import CustomUserSerializer, CustomAuthTokenSerializer, \
    UserProfileSerializer, ProfileTypeSerializer, ProfileSoundSerializer, UserReferalsSerializer, \
    ReferalsPointsSerializer
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
                'referal_code': openapi.Schema(type=openapi.TYPE_STRING, description='Optional referral code tg_id')
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
        referal_code = request.data.get("referal_code", "")
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

            defaults = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'avatar': image_url if image_url else None
            }

            user, created = CustomUser.objects.update_or_create(
                tg_id=telegram_id,
                defaults=defaults
            )

            if referal_code and referal_code.isdigit():
                try:
                    inviter = get_object_or_404(CustomUser, tg_id=int(referal_code))
                    already_referred = Referals.objects.filter(user=user, invited_user=inviter).exists()
                    if not already_referred:
                        inviter_profile = inviter.profile.first()
                        with transaction.atomic():
                            Referals.objects.create(
                                user=user,
                                invited_user=inviter
                            )
                            referal_point = ReferalsPoints.objects.first()
                            if referal_point and inviter_profile:
                                inviter_profile.coin += referal_point.points
                                inviter_profile.save()
                            elif not referal_point:
                                return Response({'error': 'Баллы рефералов не найдены'},
                                                status=status.HTTP_400_BAD_REQUEST)

                except ObjectDoesNotExist:
                    pass

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
                schema=CustomUserSerializer(),
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


class UserProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Retrieve a list of user profiles",
        responses={
            200: openapi.Response(
                description='User profiles retrieved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'profiles': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'name': openapi.Schema(type=openapi.TYPE_STRING, description='Profile name'),
                                    'image': openapi.Schema(type=openapi.TYPE_STRING, description='Profile image URL',
                                                            nullable=True),
                                    'coin_level': openapi.Schema(type=openapi.TYPE_STRING, description='Coin level'),
                                    'users_data': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                                                'tg_id': openapi.Schema(type=openapi.TYPE_STRING,
                                                                        description='Telegram ID'),
                                                'username': openapi.Schema(type=openapi.TYPE_STRING,
                                                                           description='Username'),
                                                'first_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                             description='First name', nullable=True),
                                                'last_name': openapi.Schema(type=openapi.TYPE_STRING,
                                                                            description='Last name', nullable=True),
                                                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email',
                                                                        nullable=True),
                                                'avatar': openapi.Schema(type=openapi.TYPE_STRING,
                                                                         description='Avatar URL', nullable=True),
                                                'user_profile': openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        'uuid': openapi.Schema(type=openapi.TYPE_STRING,
                                                                               format=openapi.FORMAT_UUID,
                                                                               description='Profile UUID'),
                                                        'profile_type': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                       description='Profile type'),
                                                        'coin': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                               description='Coin balance'),
                                                        'coin_level': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                     description='Coin level'),
                                                        'earn_per_tab': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                       description='Earn per tap'),
                                                        'profit_per_hour': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                                                          description='Profit per hour'),
                                                        'image': openapi.Schema(type=openapi.TYPE_STRING,
                                                                                description='Profile image URL',
                                                                                nullable=True),
                                                    },
                                                    nullable=True
                                                ),
                                                'user_rank': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                            description='User rank', nullable=True),
                                                'is_sound': openapi.Schema(type=openapi.TYPE_BOOLEAN,
                                                                           description='Sound setting'),
                                                'profile_level': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                                                description='Profile level',
                                                                                nullable=True),
                                            }
                                        )
                                    ),
                                }
                            )
                        )
                    }
                )
            )
        }
    )
    def get(self, request):
        base_url = request.build_absolute_uri('/')

        profiles = UserProfile.objects.select_related('user').all()

        profile_type_data = {}
        for profile in profiles:
            profile_type = profile.profile_type
            if profile_type not in profile_type_data:
                image_url = (
                    urljoin(base_url, profile.image.url)
                    if profile.image and hasattr(profile.image, 'url')
                    else None
                )

                profile_type_data[profile_type] = {
                    'name': profile_type,
                    'image': image_url,
                    'coin_level': profile.coin_level,
                    'users': []
                }
            if profile.user:
                profile_type_data[profile_type]['users'].append(profile.user)

        result = []
        for profile_type, _ in UserProfile.UserProfileType.choices:
            if profile_type in profile_type_data:
                data = profile_type_data[profile_type]
                sorted_users = sorted(
                    data['users'],
                    key=lambda user: user.profile.first().coin if user.profile.exists() else 0
                )
                data['users_data'] = sorted_users
                del data['users']
            else:
                image_name = UserProfile.PROFILE_TYPE_TO_IMAGE.get(profile_type, 'first.png')
                image_path = os.path.join(settings.MEDIA_URL, 'profile_type', image_name)
                image_url = urljoin(base_url, image_path)
                data = {
                    'name': profile_type,
                    'image': image_url,
                    'coin_level': UserProfile.CoinLevel.first_choice,
                    'users_data': []
                }
            result.append(data)

        serializer = ProfileTypeSerializer(result, many=True, context={'request': request})
        return Response(serializer.data)


class UserCoinUpdatedView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Update the user's coin balance",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['coin_point'],
            properties={
                'coin_point': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of coin points to add')
            }
        ),
        responses={
            200: openapi.Response(
                description='Coin balance updated successfully',
                schema=UserProfileSerializer,
                examples={
                    'application/json': {
                        'coin': 100,
                        'earn_per_tab': 12,
                        'profit_per_hour': 0.5,
                        'profile_type': 'FIPT Youtube',
                        'image': 'https://example.com/image.jpg'
                    }
                }
            ),
            400: openapi.Response(
                description='Bad request',
                examples={
                    'application/json': {
                        'error': 'coin_point is required.'
                    }
                }
            ),
            404: openapi.Response(
                description='User profile not found',
                examples={
                    'application/json': {
                        'error': 'User profile not found'
                    }
                }
            )
        }
    )
    def patch(self, request, *args, **kwargs):
        user = request.user

        coin_point = request.data.get('coin_point')

        if coin_point is None:
            return Response({"error": "coin_point is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = get_object_or_404(UserProfile, user=user)

        user_profile.coin = user_profile.coin + (user_profile.earn_per_tab * coin_point)
        user_profile.save()

        serializer = UserProfileSerializer(user_profile, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileSoundView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Update the user's profile sound",
        request_body=ProfileSoundSerializer,
        responses={
            200: openapi.Response(
                description='Profile sound updated successfully',
                schema=CustomUserSerializer,
            ),
            400: "Bad Request",
        }
    )
    def patch(self, request, *args, **kwargs):
        serializer = ProfileSoundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sound = serializer.validated_data['sound']
        user = request.user
        user.is_sound = sound
        user.save()

        return Response(CustomUserSerializer(user, context={'request': request}).data, status=status.HTTP_200_OK)


class UserReferalsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Retrieve the referral information of the authenticated user",
        responses={
            200: openapi.Response(
                description='Referral information retrieved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'referrals': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'invited_user': openapi.Schema(type=openapi.TYPE_STRING, description='Invited user ID'),
                                    'created_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Creation date')
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(description='User profile not found')
        }
    )
    def get(self, request):
        user = request.user
        referrals = Referals.objects.filter(user=user).select_related('invited_user')

        serializer = UserReferalsSerializer(referrals, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferalsPointsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=['Account'],
        operation_description="Retrieve global referral points",
        responses={
            200: openapi.Response(
                description='Referral points retrieved successfully',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'referral_points': openapi.Schema(
                            type=openapi.TYPE_NUMBER,
                            format='float',
                            description='Referral points'
                        )
                    }
                )
            ),
            404: openapi.Response(description='Referral points not found')
        }
    )
    def get(self, request):
        referral_points = ReferalsPoints.objects.all()
        serializer = ReferalsPointsSerializer(referral_points, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
