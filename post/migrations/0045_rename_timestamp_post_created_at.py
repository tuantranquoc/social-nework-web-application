# Generated by Django 3.2.3 on 2021-06-12 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0044_auto_20210606_0043'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='timestamp',
            new_name='created_at',
        ),
    ]
