# Generated by Django 5.2 on 2025-04-23 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_rename_name_country_arabic_name_country_english_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='status',
            field=models.BooleanField(default=1),
        ),
    ]
