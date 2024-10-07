# Generated by Django 5.1.1 on 2024-10-04 12:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0009_athlete_qr_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='athlete',
            name='bursary',
            field=models.FileField(blank=True, null=True, upload_to='certificates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AddField(
            model_name='athlete',
            name='sponsorship',
            field=models.CharField(blank=True, choices=[('School sponsored', 'School sponsored'), ('Parent sponsored', 'Parent sponsored')], max_length=25, null=True),
        ),
        migrations.AddField(
            model_name='athlete',
            name='student_visa',
            field=models.FileField(blank=True, null=True, upload_to='certificates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='refugee_card',
            field=models.FileField(blank=True, null=True, upload_to='certificates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='student_pass',
            field=models.FileField(blank=True, null=True, upload_to='certificates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='uneb_eq_results',
            field=models.FileField(blank=True, null=True, upload_to='certificates/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
