# Generated by Django 5.2.1 on 2025-05-12 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
