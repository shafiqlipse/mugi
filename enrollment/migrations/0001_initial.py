# Generated by Django 5.1.1 on 2024-10-11 06:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('school', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('championship', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_enrollments', to='accounts.championship')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='school.school')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='athlete_enrollments', to='accounts.sport')),
            ],
        ),
        migrations.CreateModel(
            name='AthleteEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('athletes', models.ManyToManyField(to='school.athlete')),
                ('school_enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='athlete_enrollments', to='enrollment.schoolenrollment')),
            ],
        ),
    ]
