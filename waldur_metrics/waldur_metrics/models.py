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
