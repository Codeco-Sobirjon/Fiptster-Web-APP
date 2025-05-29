from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule, ClockedSchedule, SolarSchedule

from apps.account.models import CustomUser, UserProfile, ChannelsUser, ConnectToChannel, Referals, ReferalsPoints
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site


class ReferalsInline(admin.TabularInline):
    model = Referals
    fk_name = 'invited_user'
    extra = 0
    fields = ["invited_user"]


class ConnectToChannelInline(admin.TabularInline):
    model = ConnectToChannel
    extra = 0
    readonly_fields = ('channel_info',)

    def channel_info(self, obj):
        if obj.channel:
            return f"{obj.channel.channel_type} - {obj.channel.task_type} - {obj.channel.channel_name}"
        return "-"
    channel_info.short_description = "Channel Info"


class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 0
    readonly_fields = ('image_preview',)
    fields = ('profile_type', 'coin', 'coin_level', 'earn_per_tab', 'profit_per_hour', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Превью"


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'tg_id', 'email', 'first_name', 'last_name', 'is_staff')

    fieldsets = (
        (None, {'fields': ('tg_id', 'username', 'password', 'avatar')}),
        ('Персональная информация',
         {'fields': ('first_name', 'last_name', 'email')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Группы и права', {'fields': ('groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'avatar',
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
    )

    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [UserProfileInline, ConnectToChannelInline, ReferalsInline]


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = _("Fiptster Администрации Панель. ")
admin.site.site_title = _("Fiptster Панель управления.")
admin.site.index_title = _("Добро пожаловать в админку Fiptster.")

admin.site.unregister(Site)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)

admin.site.register(UserProfile)


@admin.register(ChannelsUser)
class ChannelsUserAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'channel_name', 'channel_link')
    search_fields = ('channel_name', 'secret_code')
    list_filter = ('task_type',)

    def channel_link(self, obj):
        return mark_safe(f'<a href="{obj.channel_url}" target="_blank">{obj.channel_url}</a>')

    channel_link.short_description = "Ссылка на канал"

    class Media:
        js = ('admin/js/secret_code_toggle.js',)


@admin.register(ReferalsPoints)
class ReferalsPointsAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'points', 'created_at')
    list_filter = ('created_at',)
