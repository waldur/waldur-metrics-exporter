import datetime

from dateutil.relativedelta import relativedelta

from waldur_metrics import models, waldur_models


def fill_out(new):
    def date_iterator(start, end):
        current = start + relativedelta(months=1)

        while current < end:
            yield current
            current += relativedelta(months=1)

    prev = (
        models.ResourceLimit.objects.filter(
            resource_uuid=new.resource_uuid,
            limit_name=new.limit_name,
            date__lt=new.date,
        )
        .order_by('-date')
        .first()
    )

    if not prev:
        return

    for m in date_iterator(prev.date, new.date):
        fill_limit = models.ResourceLimit.objects.create(
            **{
                field.name: getattr(prev, field.name)
                for field in prev._meta.fields
                if field.name != 'id' and field.name != 'date'
            },
            date=datetime.date(year=m.year, month=m.month, day=1)
        )
        print(
            'Limit for filling out has been added. Resource UUID: %s, date: %s, limit: %s, value: %s.'
            % (
                fill_limit.resource_uuid,
                fill_limit.date,
                fill_limit.limit_name,
                fill_limit.limit_value,
            )
        )


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
        .order_by('resource_id', 'order__approved_at')
    )

    if not force:
        items = items.filter(
            order__approved_at__lt=datetime.date.today() - datetime.timedelta(days=100)
        )

    for item in items:
        for name, value in item.limits.items():
            limit, created = models.ResourceLimit.objects.update_or_create(
                resource_name=item.resource.name,
                resource_uuid=item.resource.uuid.hex.replace('-', ''),
                project_name=item.resource.project.name,
                project_uuid=item.resource.project.uuid.hex.replace('-', ''),
                customer_name=item.resource.project.customer.name,
                customer_uuid=item.resource.project.customer.uuid.hex.replace('-', ''),
                date=item.order.approved_at.date(),
                limit_name=name,
                defaults={
                    'limit_value': value,
                },
            )

            if created:
                fill_out(limit)
                print(
                    'Limit has been added. Resource UUID: %s, date: %s, limit: %s, value: %s.'
                    % (
                        limit.resource_uuid,
                        limit.date,
                        limit.limit_name,
                        limit.limit_name,
                    )
                )
