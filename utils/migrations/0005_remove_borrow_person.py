# Generated by Django 5.0.7 on 2024-08-14 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0004_alter_borrow_something'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='borrow',
            name='person',
        ),
    ]
