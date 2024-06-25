from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """

    created = AutoCreatedField(_('created'))
    modified = AutoLastModifiedField(_('modified'))

    def save(self, *args, **kwargs):
        """
        Overriding the save method in order to make sure that
        modified field is updated even if it is not given as
        a parameter to the update field argument.
        """
        update_fields = kwargs.get('update_fields', None)
        if update_fields:
            kwargs['update_fields'] = set(update_fields).union({'modified'})

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class AggregatedCountryLimitMetric(TimeStampedModel):
    date = models.DateField()
    country = models.CharField(max_length=7)
    component_type = models.CharField(max_length=255)
    usage_during_month = models.IntegerField()
    usage_since_beginning_of_year = models.IntegerField()

    class Meta:
        db_table = 'aggregated_country_limit_metrics'


class AggregatedCountryUsageMetric(TimeStampedModel):
    date = models.DateField()
    country = models.CharField(max_length=7)
    component_type = models.CharField(max_length=255)
    usage_during_month = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    usage_since_beginning_of_year = models.DecimalField(
        default=0, decimal_places=2, max_digits=20
    )

    class Meta:
        db_table = 'aggregated_country_usage_metrics'


class AggregatedCountryQuotaMetric(TimeStampedModel):
    date = models.DateField()
    country = models.CharField(max_length=7)
    quota_name = models.CharField(max_length=255)
    quota = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'aggregated_country_quota_metrics'


class ResourceLimit(TimeStampedModel):
    date = models.DateField()
    resource_name = models.CharField(max_length=255)
    resource_uuid = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    project_uuid = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_uuid = models.CharField(max_length=255)
    limit_name = models.CharField(max_length=255)
    limit_value = models.IntegerField()

    class Meta:
        db_table = 'resource_limits'


class ResourceUsage(TimeStampedModel):
    date = models.DateField()
    resource_name = models.CharField(max_length=255)
    resource_uuid = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255)
    project_uuid = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_uuid = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    usage = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    usage_since_creation = models.DecimalField(
        default=0, decimal_places=2, max_digits=20
    )

    class Meta:
        db_table = 'resource_usages'
        unique_together = (
            'date',
            'resource_uuid',
            'project_uuid',
            'customer_uuid',
            'type',
        )
