from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0015_littleflow_id_alter_littleflow_activity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='littleflow',
            old_name='offered_calls',
            new_name='incoming_calls',
        )
    ]