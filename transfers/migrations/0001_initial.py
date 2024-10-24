# Generated by Django 5.1.1 on 2024-10-11 06:55

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('school', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('documents', models.FileField(blank=True, null=True, upload_to='transfer_documents/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('approved', 'Approved')], default='pending', max_length=10)),
                ('requested_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('approved_at', models.DateTimeField(blank=True, null=True)),
                ('approver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfer_approver', to=settings.AUTH_USER_MODEL)),
                ('athlete', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transferred_athlete', to='school.athlete')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owning_school', to='school.school')),
                ('requester', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='requesting_school', to='school.school')),
            ],
        ),
    ]
