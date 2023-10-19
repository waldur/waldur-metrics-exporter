import calendar
import datetime

from dateutil.relativedelta import relativedelta

from waldur_metrics import models, waldur_models


def date_iterator(start, end):
    current = start

    while current <= end:
        yield (
            datetime.date(year=current.year, month=current.month, day=1),
            datetime.date(
                year=current.year,
                month=current.month,
                day=calendar.monthrange(current.year, current.month)[1],
            ),
        )
        current = current + relativedelta(months=1)


def create_limits(item):
    result = []

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
            print(
                'Limit has been added. Resource UUID: %s, date: %s, limit: %s, value: %s.'
                % (
                    limit.resource_uuid,
                    limit.date,
                    limit.limit_name,
                    limit.limit_name,
                )
            )
        result.append(limit)

    return result


def copy_limits(previous, start):
    result = []

    for limit in previous:
        fill_limit = models.ResourceLimit.objects.create(
            **{
                field.name: getattr(limit, field.name)
                for field in limit._meta.fields
                if field.name != 'id' and field.name != 'date'
            },
            date=datetime.date(year=start.year, month=start.month, day=1)
        )

        print(
            'Limit has been copied. Resource UUID: %s, date: %s, limit: %s, value: %s.'
            % (
                fill_limit.resource_uuid,
                fill_limit.date,
                fill_limit.limit_name,
                fill_limit.limit_value,
            )
        )
        result.append(fill_limit)

    return result


def update_resource_limits(force=False):
    now = datetime.datetime.now()
    print('Start: %s' % now)

    if force:
        models.ResourceLimit.objects.all().delete()

    if not models.ResourceLimit.objects.count():
        force = True

    resources = (
        waldur_models.Resource.objects.using('waldur')
        .exclude(limits={}, state=waldur_models.Resource.States.CREATING)
        .order_by('id', 'created')
    )

    if not force:
        terminate_resource_uuids = set(
            waldur_models.OrderItem.objects.using('waldur')
            .filter(
                state=waldur_models.OrderItem.States.DONE,
                type=waldur_models.OrderItem.Types.TERMINATE,
            )
            .values_list('resource__uuid', flat=True)
        )
        resources = resources.exclude(uuid__in=terminate_resource_uuids)

    for resource in resources:
        terminated_date = None
        previous = None

        if force:
            terminate_item = (
                waldur_models.OrderItem.objects.using('waldur')
                .filter(
                    resource_id=resource.id,
                    state=waldur_models.OrderItem.States.DONE,
                    type=waldur_models.OrderItem.Types.TERMINATE,
                )
                .first()
            )

            if terminate_item:
                terminated_date = terminate_item.order.approved_at.replace(tzinfo=None)

        created_date = resource.created.replace(tzinfo=None)

        for start, end in date_iterator(
            created_date if force else now, terminated_date or now
        ):
            print(
                'Sync resource: %s, from: %s, to: %s created: %s, terminated: %s'
                % (resource.uuid.hex, start, end, created_date, terminated_date)
            )

            item = (
                waldur_models.OrderItem.objects.using('waldur')
                .filter(
                    state=waldur_models.OrderItem.States.DONE,
                    type__in=[
                        waldur_models.OrderItem.Types.CREATE,
                        waldur_models.OrderItem.Types.UPDATE,
                    ],
                    resource_id=resource.id,
                    order__approved_at__gte=start,
                    order__approved_at__lte=end,
                )
                .exclude(limits={})
                .order_by('-order__approved_at')
            ).first()

            if item:
                previous = create_limits(item)
            elif previous and previous[0].resource_uuid == resource.uuid.hex:
                copy_limits(previous, start)
            else:
                print(
                    'Sync of resource has been skipped because item and previous item are not found. '
                    'Resource %s, state %s, from %s, to %s.'
                    % (resource.uuid.hex, resource.get_state_display(), start, end)
                )
                continue

    print('End: %s' % datetime.datetime.now())
