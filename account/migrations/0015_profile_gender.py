# Generated by Django 5.1.2 on 2024-11-24 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_transaction_sender_email_alter_transaction_sender'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
    ]