# Generated by Django 5.1.1 on 2024-11-16 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_alter_athlete_sport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athlete',
            name='student_pass_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='athlete',
            name='uneb_code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]