# Generated by Django 5.1.2 on 2024-11-13 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_paymentmethod_type_alter_paymentmethod_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]