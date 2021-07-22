# Generated by Django 3.2.3 on 2021-07-22 14:47

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0047_auto_20210615_0155'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='viewed',
            field=models.ManyToManyField(blank=True, related_name='p_view', to=settings.AUTH_USER_MODEL),
        ),
    ]
