from waldur_metrics import models, waldur_models


def update_resource_limits(force=False):
    if force:
        models.ResourceLimit.objects.all().delete()

    items = (
        waldur_models.OrderItem.objects.using('waldur')
        .filter(
            state=waldur_models.OrderItem.States.DONE,
            type__in=[
                waldur_models.OrderItem.Types.CREATE,
                waldur_models.OrderItem.Types.UPDATE,
            ],
        )
        .exclude(limits={})
        .order_by('order__approved_at')
    )
    for item in items:
        for name, value in item.limits.items():
            obj, created = models.ResourceLimit.objects.update_or_create(
                resource_name=item.resource.name,
                resource_uuid=item.resource.uuid.hex.replace('-', ''),
                project_name=item.resource.project.name,
                project_uuid=item.resource.project.uuid.hex.replace('-', ''),
                customer_name=item.resource.project.customer.name,
                customer_uuid=item.resource.project.customer.uuid.hex.replace('-', ''),
                date=item.order.approved_at,
                limit_name=name,
                defaults={
                    'limit_value': value,
                },
            )

            if created:
                print(
                    'Limit has been added. Resource UUID: %s, date: %s, limit: %s, value: %s.'
                    % (item.resource.uuid, item.order.approved_at, name, value)
                )
