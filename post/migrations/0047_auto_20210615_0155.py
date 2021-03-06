# Generated by Django 3.2.3 on 2021-06-14 18:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0046_rename_created_at_post_timestamp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='uservote',
            old_name='report',
            new_name='down_vote',
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
