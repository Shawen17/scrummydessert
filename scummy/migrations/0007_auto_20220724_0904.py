# Generated by Django 3.1.13 on 2022-07-24 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scummy', '0006_auto_20220724_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='items',
            field=models.TextField(null=True),
        ),
    ]
