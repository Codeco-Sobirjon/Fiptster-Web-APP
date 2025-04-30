from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account.models import CustomUser
from apps.account.serializers import TelegramLoginSerializer
from apps.account.utils.telegram_auth import verify_telegram_auth


class TelegramLoginView(APIView):
    def post(self, request):
        serializer = TelegramLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if not verify_telegram_auth(data.copy(), settings.TELEGRAM_BOT_TOKEN):
            return Response({"detail": "Invalid Telegram authentication"}, status=status.HTTP_400_BAD_REQUEST)

        tg_id = data['id']
        user, created = CustomUser.objects.get_or_create(tg_id=tg_id, defaults={
            'username': data.get('username', f'tg{tg_id}'),
            'first_name': data.get('first_name', ''),
            'last_name': data.get('last_name', ''),
        })

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
