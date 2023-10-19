from django.db import models
from django.utils.translation import gettext_lazy as _
from django_fsm import FSMIntegerField

from waldur_metrics.models import TimeStampedModel


class Customer(models.Model):
    uuid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=2)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'structure_customer'


class Project(TimeStampedModel):
    uuid = models.CharField(max_length=255)
    customer = models.ForeignKey(
        Customer,
        verbose_name=_('organization'),
        related_name='projects',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'structure_project'


class Resource(TimeStampedModel):
    class States:
        CREATING = 1
        OK = 2
        ERRED = 3
        UPDATING = 4
        TERMINATING = 5
        TERMINATED = 6

        CHOICES = (
            (CREATING, 'Creating'),
            (OK, 'OK'),
            (ERRED, 'Erred'),
            (UPDATING, 'Updating'),
            (TERMINATING, 'Terminating'),
            (TERMINATED, 'Terminated'),
        )

    uuid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    limits = models.JSONField(blank=True, default=dict)
    state = FSMIntegerField(default=States.CREATING, choices=States.CHOICES)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'marketplace_resource'


class Order(TimeStampedModel):
    approved_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'marketplace_order'


class OrderItem(TimeStampedModel):
    class Types:
        CREATE = 1
        UPDATE = 2
        TERMINATE = 3

        CHOICES = (
            (CREATE, 'Create'),
            (UPDATE, 'Update'),
            (TERMINATE, 'Terminate'),
        )

    class States:
        PENDING = 1
        EXECUTING = 2
        DONE = 3
        ERRED = 4
        TERMINATED = 5
        TERMINATING = 6

        CHOICES = (
            (PENDING, 'pending'),
            (EXECUTING, 'executing'),
            (DONE, 'done'),
            (ERRED, 'erred'),
            (TERMINATED, 'terminated'),
            (TERMINATING, 'terminating'),
        )

        TERMINAL_STATES = {DONE, ERRED, TERMINATED}

    resource = models.ForeignKey(
        on_delete=models.CASCADE, to=Resource, null=True, blank=True
    )
    order = models.ForeignKey(on_delete=models.CASCADE, to=Order, related_name='items')
    state = FSMIntegerField(default=States.PENDING, choices=States.CHOICES)
    type = models.PositiveSmallIntegerField(choices=Types.CHOICES, default=Types.CREATE)
    limits = models.JSONField(blank=True, default=dict)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'marketplace_orderitem'


class OfferingComponent(models.Model):
    type = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'marketplace_offeringcomponent'


class ComponentUsage(TimeStampedModel):
    resource = models.ForeignKey(
        on_delete=models.CASCADE, to=Resource, related_name='usages'
    )
    component = models.ForeignKey(
        on_delete=models.CASCADE,
        to=OfferingComponent,
    )
    usage = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    date = models.DateTimeField()

    def save(self, *args, **kwargs):
        pass

    class Meta:
        managed = False
        db_table = 'marketplace_componentusage'
