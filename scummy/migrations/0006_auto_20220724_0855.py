# Generated by Django 3.1.13 on 2022-07-24 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scummy', '0005_auto_20220723_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='state',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
