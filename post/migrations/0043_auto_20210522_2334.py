# Generated by Django 3.2.3 on 2021-05-22 16:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0042_auto_20210516_0145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='vote',
        ),
        migrations.AddField(
            model_name='uservote',
            name='post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.post'),
        ),
    ]