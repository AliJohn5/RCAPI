# Generated by Django 5.2 on 2025-06-12 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0011_postimage_is_for_web_and_app'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postimage',
            name='is_for_web_and_app',
        ),
        migrations.AddField(
            model_name='post',
            name='is_for_web_and_app',
            field=models.BooleanField(default=False),
        ),
    ]
