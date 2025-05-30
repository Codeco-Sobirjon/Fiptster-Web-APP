# Generated by Django 5.2 on 2025-05-24 16:04

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_alter_customuser_avatar_alter_userprofile_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_sound',
            field=models.BooleanField(default=True, verbose_name='Звук включен'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('4e7b1947-fddc-46ba-a297-c1dcfd5ada50'), editable=False, primary_key=True, serialize=False, verbose_name='UUID'),
        ),
    ]
