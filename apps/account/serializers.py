from rest_framework import serializers


class TelegramLoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    photo_url = serializers.CharField(required=False)
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()
