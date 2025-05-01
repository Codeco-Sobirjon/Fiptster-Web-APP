import json
import urllib

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import CustomUser
from apps.account.serializers import TelegramLoginSerializer
from apps.account.utils.telegram_auth import check_auth, TOKEN


class TelegramAuthAPIView(APIView):
    permission_classes = [AllowAny]

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

            user = CustomUser.objects.filter(telegram_id=telegram_id).first()

            user, created = CustomUser.objects.update_or_create(
                tg_id=telegram_id,
                defaults={
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name
                }
            )

            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)

        except json.JSONDecodeError:
            return Response({'error': 'Неверный формат JSON'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Ошибка сервера: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
