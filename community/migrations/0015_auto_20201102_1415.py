# Generated by Django 3.0.6 on 2020-11-02 07:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0014_auto_20201102_1046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='community',
            old_name='time_stamp',
            new_name='timestamp',
        ),
    ]
