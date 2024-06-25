import datetime

import pytz
from django.db.models import Sum

from waldur_metrics import models, waldur_models
from waldur_metrics.utils_resource_limits import resource_date_iterator


def get_prev_value(resource, usage_type, date):
    prev = (
        models.ResourceUsage.objects.filter(
            resource_uuid=resource.uuid.hex.replace('-', ''),
            type=usage_type,
            date__lt=date,
        )
        .order_by('-date')
        .first()
    )

    if not prev:
        return 0

    return prev.usage_since_creation


def create_usage(usage, resource, usage_type, date):
    usage, created = models.ResourceUsage.objects.update_or_create(
        resource_uuid=resource.uuid.hex.replace('-', ''),
        project_uuid=resource.project.uuid.hex.replace('-', ''),
        customer_uuid=resource.project.customer.uuid.hex.replace('-', ''),
        date=date,
        type=usage_type,
        defaults={
            'resource_name': resource.name,
            'project_name': resource.project.name,
            'customer_name': resource.project.customer.name,
            'usage_since_creation': get_prev_value(resource, usage_type, date) + usage,
            'usage': usage,
        },
    )

    if created:
        print(
            'Usage has been added. Resource UUID: %s, date: %s, type: %s, value: %s.'
            % (
                resource.uuid.hex,
                date,
                usage_type,
                usage,
            )
        )

    return usage


def copy_usage(previous, date):
    usage = models.ResourceUsage.objects.filter(
        resource_uuid=previous.resource_uuid,
        project_uuid=previous.project_uuid,
        customer_uuid=previous.customer_uuid,
        type=previous.type,
        date=date,
    ).first()

    if usage:
        return usage

    usage = models.ResourceUsage.objects.create(
        **{
            field.name: getattr(previous, field.name)
            for field in previous._meta.fields
            if field.name != 'id' and field.name != 'date'
        },
        date=date
    )

    print(
        'Usage has been copied. Resource UUID: %s, date: %s, type: %s, usage: %s, since_creation: %s.'
        % (
            usage.resource_uuid,
            usage.date,
            usage.type,
            usage.usage,
            usage.usage_since_creation,
        )
    )

    return usage


def update_resource_usages(force=False):
    previous = None

    for resource, start, end, created_date, terminated_date in resource_date_iterator(
        force, models.ResourceUsage
    ):
        print(
            'Sync resource: %s, from: %s, to: %s created: %s, terminated: %s'
            % (resource.uuid.hex, start, end, created_date, terminated_date)
        )

        types = list(resource.limits.keys())

        for usage_type in types:
            usage = (
                waldur_models.ComponentUsage.objects.using('waldur')
                .filter(
                    resource_id=resource.id,
                    component__type=usage_type,
                    date__gte=pytz.utc.localize(start),
                    date__lte=pytz.utc.localize(end),
                )
                .order_by('-date')
            ).aggregate(Sum("usage"))['usage__sum']

            if usage is not None:
                print(usage, resource.id, usage_type, start, end)

            if usage is not None:
                previous = create_usage(usage, resource, usage_type, start)
            elif (
                previous
                and previous.resource_uuid == resource.uuid.hex
                and previous.type == usage_type
            ):
                copy_usage(previous, start)
            else:
                # print(
                #     'Sync of resource has been skipped because item and previous item are not found. '
                #     'Resource %s, state %s, from %s, to %s.'
                #     % (resource.uuid.hex, resource.get_state_display(), start, end)
                # )
                continue

    print('End: %s' % datetime.datetime.now())
