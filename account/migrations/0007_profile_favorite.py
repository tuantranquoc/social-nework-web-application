# Generated by Django 3.2.3 on 2021-07-19 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0047_auto_20210615_0155'),
        ('account', '0006_delete_followerrelation'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite',
            field=models.ManyToManyField(blank=True, to='post.Post'),
        ),
    ]