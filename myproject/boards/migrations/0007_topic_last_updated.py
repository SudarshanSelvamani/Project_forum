# Generated by Django 3.2.5 on 2021-07-15 15:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0006_remove_topic_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='last_updated',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]