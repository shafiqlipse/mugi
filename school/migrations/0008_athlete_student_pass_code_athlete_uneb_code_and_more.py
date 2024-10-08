# Generated by Django 5.1.1 on 2024-09-28 04:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0007_alter_athlete_ple_certificate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='student_pass_code',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='athlete',
            name='uneb_code',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='athlete',
            name='uneb_eq_results',
            field=models.FileField(blank=True, null=True, upload_to='athlete_photos/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
