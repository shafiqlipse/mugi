# Generated by Django 5.1.1 on 2024-09-25 07:58

import school.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0004_athlete_nationality_athlete_refugee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='index_number',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[school.models.validate_index_number]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='lin',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='ple_certificate',
            field=models.ImageField(blank=True, null=True, upload_to='certificates/'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='refugee_card',
            field=models.ImageField(blank=True, null=True, upload_to='athlete_photos/'),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='relationship',
            field=models.CharField(choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Other', 'Other')], default=1, max_length=15),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='athlete',
            name='student_pass',
            field=models.ImageField(blank=True, null=True, upload_to='athlete_photos/'),
        ),
    ]
