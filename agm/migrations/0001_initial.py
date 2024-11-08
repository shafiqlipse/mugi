# Generated by Django 5.1.1 on 2024-11-04 13:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delegates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('photo', models.ImageField(upload_to='agm_photo/')),
                ('contact', models.CharField(max_length=15)),
                ('school', models.CharField(max_length=125)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], max_length=14)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='district', to='accounts.district')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agm_region', to='accounts.region')),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agm_zone', to='accounts.zone')),
            ],
        ),
    ]