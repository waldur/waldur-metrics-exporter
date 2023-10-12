from waldur_metrics import models, waldur_models


def get_prev_value(usage):
    prev = (
        models.ResourceUsage.objects.filter(
            resource_uuid=usage.resource.uuid.hex.replace('-', ''),
            type=usage.component.type,
        )
        .order_by('-date')
        .first()
    )

    if not prev:
        return 0

    return prev.usage_since_creation


def update_resource_usages(force=False):
    if force:
        models.ResourceUsage.objects.all().delete()

    usages = waldur_models.ComponentUsage.objects.using('waldur').order_by('date')

    for usage in usages:
        if not usage.usage:
            continue

        prev_usage = get_prev_value(usage)
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
                'usage_since_creation': prev_usage + usage.usage,
            },
        )

        if created:
            print(
                'Usage has been added. Resource ID: %s, date: %s, type: %s, value: %s, since creation: %s'
                % (
                    usage.resource_id,
                    usage.date,
                    usage.component.type,
                    usage.usage,
                    prev_usage + usage.usage,
                )
            )
