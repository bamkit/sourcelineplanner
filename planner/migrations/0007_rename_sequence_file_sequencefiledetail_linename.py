# Generated by Django 5.1.1 on 2024-09-17 01:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0006_remove_gunentry_p190_file_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sequencefiledetail',
            old_name='sequence_file',
            new_name='linename',
        ),
    ]
