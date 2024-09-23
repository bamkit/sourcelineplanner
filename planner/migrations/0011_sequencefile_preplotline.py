# Generated by Django 5.1.1 on 2024-09-23 00:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0010_points_delete_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequencefile',
            name='preplotline',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sequence', to='planner.preplotline'),
        ),
    ]