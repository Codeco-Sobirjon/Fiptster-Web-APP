# Generated by Django 5.2 on 2025-05-13 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='type',
            field=models.CharField(choices=[('reels', 'Reels'), ('advertisement', 'Advertisement')], default='reels', max_length=255, verbose_name='Тип'),
        ),
    ]
