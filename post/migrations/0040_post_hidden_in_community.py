# Generated by Django 3.0.7 on 2021-05-15 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0034_auto_20210507_1918'),
        ('post', '0039_post_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hidden_in_community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hidden_in_coomunity', to='community.Community'),
        ),
    ]