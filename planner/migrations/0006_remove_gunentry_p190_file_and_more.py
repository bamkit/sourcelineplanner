# Generated by Django 5.1.1 on 2024-09-16 23:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0005_sequencefile_rename_p190line_preplotline_gunentry_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gunentry',
            name='p190_file',
        ),
        migrations.RemoveField(
            model_name='sourceentry',
            name='p190_file',
        ),
        migrations.RemoveField(
            model_name='vesselentry',
            name='p190_file',
        ),
        migrations.AddField(
            model_name='sequencefile',
            name='linename',
            field=models.CharField(default='default', max_length=255),
        ),
        migrations.CreateModel(
            name='SequenceFileDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sp', models.IntegerField()),
                ('lat', models.FloatField()),
                ('long', models.FloatField()),
                ('east', models.FloatField()),
                ('north', models.FloatField()),
                ('depth', models.FloatField()),
                ('datetime', models.DateTimeField()),
                ('ze1', models.FloatField()),
                ('zn1', models.FloatField()),
                ('ze2', models.FloatField()),
                ('zn2', models.FloatField()),
                ('ze3', models.FloatField()),
                ('zn3', models.FloatField()),
                ('mean_e', models.FloatField()),
                ('mean_n', models.FloatField()),
                ('sequence_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='detail', to='planner.sequencefile')),
            ],
        ),
        migrations.DeleteModel(
            name='EchosounderEntry',
        ),
        migrations.DeleteModel(
            name='GunEntry',
        ),
        migrations.DeleteModel(
            name='SourceEntry',
        ),
        migrations.DeleteModel(
            name='VesselEntry',
        ),
    ]