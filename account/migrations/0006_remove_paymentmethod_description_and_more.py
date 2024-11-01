# Generated by Django 5.1.2 on 2024-11-01 09:45

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_paymentmethod_accounts_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentmethod',
            name='description',
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='payment_method_image',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='payment_method_image'),
        ),
    ]
