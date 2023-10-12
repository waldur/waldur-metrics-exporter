# Generated by Django 3.2.20 on 2023-09-20 22:43

import django.utils.timezone
import model_utils.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waldur_metrics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregatedCountryQuotaMetric',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'created',
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='created',
                    ),
                ),
                (
                    'modified',
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name='modified',
                    ),
                ),
                ('date', models.DateField()),
                ('country', models.CharField(max_length=7)),
                ('quota_name', models.CharField(max_length=255)),
                ('quota', models.PositiveIntegerField(default=0)),
            ],
            options={
                'db_table': 'aggregated_country_quota_metrics',
            },
        ),
    ]