# Generated by Django 3.0.6 on 2020-11-02 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0020_auto_20201029_1958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='view',
            name='new_timestamp',
        ),
    ]
