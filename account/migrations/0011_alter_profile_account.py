# Generated by Django 5.1.2 on 2024-11-20 17:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_profile_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='account',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='account.accounts'),
        ),
    ]
