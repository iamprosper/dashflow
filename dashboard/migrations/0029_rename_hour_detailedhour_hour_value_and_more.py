# Generated by Django 5.0.4 on 2024-06-12 10:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_alter_detailedflow_hour_alter_detailedflow_mn'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detailedhour',
            old_name='hour',
            new_name='hour_value',
        ),
        migrations.RenameField(
            model_name='detailedmin',
            old_name='mn',
            new_name='mn_value',
        ),
    ]