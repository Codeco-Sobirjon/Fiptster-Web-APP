# Generated by Django 5.2 on 2025-05-29 16:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_alter_userprofile_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('6f8b83ee-5595-419e-94f5-a717bb8dbf8f'), editable=False, primary_key=True, serialize=False, verbose_name='UUID'),
        ),
    ]
