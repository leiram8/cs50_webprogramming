# Generated by Django 3.1.2 on 2021-03-31 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0008_auto_20210331_0258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='image',
            field=models.URLField(blank=True),
        ),
    ]
