# Generated by Django 3.2.3 on 2021-05-30 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0034_auto_20210507_1918'),
        ('post', '0038_auto_20210530_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='community',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='community.community'),
        ),
    ]
