# Generated by Django 3.2.3 on 2021-06-05 17:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0043_auto_20210530_1809'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='down_vote',
            field=models.ManyToManyField(blank=True, related_name='p_down_vote', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='up_vote',
            field=models.ManyToManyField(blank=True, related_name='p_up_vote', to=settings.AUTH_USER_MODEL),
        ),

    ]
