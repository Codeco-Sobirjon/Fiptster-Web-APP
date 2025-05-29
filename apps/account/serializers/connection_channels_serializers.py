from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from collections import defaultdict

from apps.account.models import CustomUser, UserProfile, ChannelsUser, ConnectToChannel
from apps.account.serializers.serializers import CustomUserSerializer


class ChannelsUserSerializer(serializers.ModelSerializer):
    is_applied = serializers.SerializerMethodField()

    class Meta:
        model = ChannelsUser
        fields = ['uuid', 'channel_name', 'channel_coin', 'channel_link', 'channel_type', 'description', 'is_applied']

    def get_is_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ConnectToChannel.objects.filter(user=request.user, channel=obj).exists()
        return False


class GroupedByTaskTypeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        grouped = defaultdict(list)

        for item in data:
            grouped[item.task_type].append(item)

        result = []
        for choice_value, _ in ChannelsUser.TaskType.choices:
            tasks = grouped.get(choice_value, [])
            result.append({
                'task_type': choice_value,
                'tasks': ChannelsUserSerializer(tasks, many=True, context=self.context).data
            })

        return result


class ChannelsUserGroupedSerializer(serializers.Serializer):
    task_type = serializers.CharField()
    tasks = ChannelsUserSerializer(many=True)

    class Meta:
        list_serializer_class = GroupedByTaskTypeSerializer



