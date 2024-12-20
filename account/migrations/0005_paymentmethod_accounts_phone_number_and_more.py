# Generated by Django 5.1.2 on 2024-10-24 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_rename_transaction_number_transaction_transaction_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('method', models.CharField(choices=[('bkash', 'Bkash'), ('nagad', 'Nagad'), ('rocket', 'Rocket'), ('all', 'Bkash, Nagad, Rocket')], default='bkash', max_length=10)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='accounts',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
