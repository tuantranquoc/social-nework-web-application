# Generated by Django 3.0.7 on 2021-03-26 15:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatv0', '0003_room_room_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='user',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
