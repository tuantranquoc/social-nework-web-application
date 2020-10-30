# Generated by Django 3.0.6 on 2020-10-29 08:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0015_auto_20201029_1528'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='type',
        ),
        migrations.AddField(
            model_name='post',
            name='type',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.PostType'),
        ),
    ]