# Generated by Django 4.2.16 on 2024-12-21 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('new_store', '0002_orderitem_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending', 'В ожидании'), ('completed', 'Завершён'), ('canceled', 'Отменён')], default='pending', max_length=10),
        ),
    ]