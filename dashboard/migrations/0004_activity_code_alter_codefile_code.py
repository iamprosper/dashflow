# Generated by Django 5.0.4 on 2024-05-03 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_codefile_remove_activity_code_call_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='code',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='codefile',
            name='code',
            field=models.IntegerField(),
        ),
    ]
