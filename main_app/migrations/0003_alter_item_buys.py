# Generated by Django 4.1.2 on 2022-10-12 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_alter_item_buys_alter_purchased_budget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='buys',
            field=models.ManyToManyField(related_name='buys', to='main_app.budget'),
        ),
    ]
