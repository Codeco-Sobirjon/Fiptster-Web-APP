from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from apps.account.models import CustomUser, UserProfile
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site


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
    list_display = ('tg_id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

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
    ordering = ('id',)
    inlines = [UserProfileInline]


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.site_header = _("Fiptster Администрации Панель. ")
admin.site.site_title = _("Fiptster Панель управления.")
admin.site.index_title = _("Добро пожаловать в админку Fiptster.")

admin.site.unregister(Site)
