# Generated by Django 3.0.6 on 2020-11-03 03:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0022_auto_20201103_0851'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='posttype',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='view',
            options={'ordering': ['-id']},
        ),
    ]