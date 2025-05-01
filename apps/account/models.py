import os

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.db import models
from apps.account.managers.custom_user import CustomUserManager
from django.utils.translation import gettext as _
from django.conf import settings


class CustomUser(AbstractBaseUser, PermissionsMixin):
    tg_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Телеграм ID")
    email = models.EmailField(unique=True, verbose_name="Электронная почта", null=True, blank=True)
    username = models.CharField(max_length=250, unique=True, verbose_name="Логин", null=True, blank=True)
    first_name = models.CharField(max_length=30, verbose_name="Имя", null=True, blank=True)
    last_name = models.CharField(max_length=30, verbose_name="Фамилия", null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_("Аватар"))
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True, verbose_name="Группы")
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_set", blank=True,
                                              verbose_name="Разрешения")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class UserProfile(models.Model):

    class UserProfileType(models.TextChoices):
        first_choice = 'Rookie Voyeur', _('Rookie Voyeur  Voyeur')
        second_choice = 'Late-Night Scroller', _('Late-Night Scroller')
        third_choice = 'Naughty Subscriber', _('Naughty Subscriber')
        fourth_choice = 'Private Teaser', _('Private Teaser')
        fifth_choice = 'Erotic Enthusiast', _('Erotic Enthusiast')
        sixth_choice = 'XXX VIP', _('XXX VIP')
        seventh_choice = 'Hardcore Legend', _('Hardcore Legend')
        eighth_choice = 'Kink Master', _('Kink Master')
        ninth_choice = 'Adult Insider', _('Adult Insider')
        tenth_choice = 'Exclusive Pleasure-Seeker', _('Exclusive Pleasure-Seeker')
        eleventh_choice = 'FIPT Legend', _('FIPT Legend')

    PROFILE_TYPE_TO_IMAGE = {
        UserProfileType.first_choice: 'first.png',
        UserProfileType.second_choice: 'second.png',
        UserProfileType.third_choice: 'third.png',
        UserProfileType.fourth_choice: 'fourth.png',
        UserProfileType.fifth_choice: 'fifth.png',
        UserProfileType.sixth_choice: 'sixth.png',
        UserProfileType.seventh_choice: 'seventh.png',
        UserProfileType.eighth_choice: 'eighth.png',
        UserProfileType.ninth_choice: 'ninth.png',
        UserProfileType.tenth_choice: 'tenth.png',
        UserProfileType.eleventh_choice: 'eleventh.png',
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile',
                             verbose_name=_("Пользователь"), null=True, blank=True)
    earn_per_tab = models.PositiveIntegerField(default=0, verbose_name=_("Заработок за вкладку"),
                                               null=True, blank=True)
    coin_level = models.PositiveIntegerField(default=0, verbose_name=_("Уровень монеты"), null=True, blank=True)
    profit_per_hour = models.FloatField(default=0, verbose_name=_("Прибыль в час"),
                                        null=True, blank=True)
    coin = models.DecimalField(max_digits=10, decimal_places=1, default=0, verbose_name=_("Монета"), null=True, blank=True)
    profile_type = models.CharField(max_length=50, choices=UserProfileType.choices,
                                     default=UserProfileType.first_choice, verbose_name=_("Тип профиля"))
    image = models.ImageField(upload_to='user_profile/', blank=True, null=True, verbose_name=_("Изображение"))

    objects = models.Manager()

    def save(self, *args, **kwargs):
        if not self.image or self._profile_type_changed():
            image_name = self.PROFILE_TYPE_TO_IMAGE.get(self.profile_type, 'first.png')
            image_path = os.path.join('profile_type', image_name)
            self.image.name = image_path
            self.coin_level = 5000
            self.earn_per_tab = 3
            self.profit_per_hour = 0.5
        super().save(*args, **kwargs)

    def _profile_type_changed(self):
        if not self.pk:
            return True
        try:
            old = UserProfile.objects.get(pk=self.pk)
            return old.profile_type != self.profile_type
        except UserProfile.DoesNotExist:
            return True

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
