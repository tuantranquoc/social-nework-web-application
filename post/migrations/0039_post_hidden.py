# Generated by Django 3.0.7 on 2021-05-15 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0038_auto_20210408_1537'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='hidden',
            field=models.BooleanField(default=False),
        ),
    ]