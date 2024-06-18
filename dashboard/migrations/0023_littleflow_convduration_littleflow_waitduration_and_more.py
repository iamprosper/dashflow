# Generated by Django 5.0.4 on 2024-06-07 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_delete_daykpiduration'),
    ]

    operations = [
        migrations.AddField(
            model_name='littleflow',
            name='convDuration',
            field=models.IntegerField(default=0, verbose_name='Total Conv Duration'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='littleflow',
            name='waitDuration',
            field=models.IntegerField(default=0, verbose_name='Total Waiting Duration'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='littleflow',
            name='wrapupDuration',
            field=models.IntegerField(default=0, verbose_name='Total WrapUp duration'),
            preserve_default=False,
        ),
    ]