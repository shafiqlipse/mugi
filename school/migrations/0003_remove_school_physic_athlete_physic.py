# Generated by Django 5.1.1 on 2024-09-20 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0002_school_physic_alter_school_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='school',
            name='physic',
        ),
        migrations.AddField(
            model_name='athlete',
            name='physic',
            field=models.CharField(blank=True, choices=[('Normal', 'Normal'), ('Special Needs', 'Special Needs')], default='Normal', max_length=25, null=True),
        ),
    ]
