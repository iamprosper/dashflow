# Generated by Django 5.0.4 on 2024-05-02 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('code_call', models.IntegerField()),
                ('code_file', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_agent', models.IntegerField()),
                ('last_name', models.CharField(max_length=200)),
                ('first_name', models.CharField(max_length=200)),
                ('activities', models.ManyToManyField(to='dashboard.activity')),
            ],
        ),
    ]
