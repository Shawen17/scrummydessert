# Generated by Django 3.1.13 on 2022-07-23 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scummy', '0004_auto_20220715_1724'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vendor',
            old_name='amount',
            new_name='amount_paid',
        ),
        migrations.AddField(
            model_name='vendor',
            name='total_amount',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='subject',
            field=models.CharField(choices=[('event planner', 'Event planner'), ('enquiry', 'Enquiry'), ('complaint', 'Complaint'), ('report', 'Report'), ('others', 'Others')], max_length=20),
        ),
    ]