from waldur_metrics import models, waldur_models


def get_prev_value(usage):
    qs = models.ResourceUsage.objects.filter(
        resource_uuid=usage.resource.uuid.hex.replace('-', ''),
        type=usage.component.type,
    ).order_by('-date')

    print('Prev all usages:')
    print(
        [
            'Resource: %s (%s), Data: %s, type: %s, usage: %s, since_creation: %s'
            % (
                p.resource_name,
                p.resource_uuid,
                p.date,
                p.type,
                p.usage,
                p.usage_since_creation,
            )
            for p in qs
        ]
    )

    prev = qs.first()

    print(
        'Prev usage:'
        'Resource: %s (%s), Data: %s, type: %s, usage: %s, since_creation: %s'
        % (
            prev.resource_name,
            prev.resource_uuid,
            prev.date,
            prev.type,
            prev.usage,
            prev.usage_since_creation,
        )
    )

    if not prev:
        return 0

    return prev.usage_since_creation


def update_resource_usages(force=False):
    if force:
        models.ResourceUsage.objects.all().delete()

    usages = waldur_models.ComponentUsage.objects.using('waldur').order_by(
        'resource_id', 'date'
    )

    for usage in usages:
        if not usage.usage:
            continue

        prev_usage = get_prev_value(usage)
        since_creation = prev_usage + usage.usage
        obj, created = models.ResourceUsage.objects.update_or_create(
            resource_name=usage.resource.name,
            resource_uuid=usage.resource.uuid.hex.replace('-', ''),
            project_name=usage.resource.project.name,
            project_uuid=usage.resource.project.uuid.hex.replace('-', ''),
            customer_name=usage.resource.project.customer.name,
            customer_uuid=usage.resource.project.customer.uuid.hex.replace('-', ''),
            date=usage.date,
            type=usage.component.type,
            defaults={
                'usage': usage.usage,
                'usage_since_creation': since_creation,
            },
        )

        print(
            'Usage has been %s. Resource UUID: %s, resource name: %s, '
            'date: %s, type: %s, value: %s, since creation: %s'
            % (
                'added' if created else 'updated',
                usage.resource.uuid.hex.replace('-', ''),
                usage.resource.name,
                usage.date,
                usage.component.type,
                usage.usage,
                since_creation,
            )
        )
