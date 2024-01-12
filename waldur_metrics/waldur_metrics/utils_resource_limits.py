import calendar
import datetime

from dateutil.relativedelta import relativedelta

from waldur_metrics import models, waldur_models


def date_iterator(start, end):
    current = start

    while current <= end:
        yield (
            datetime.datetime(
                year=current.year,
                month=current.month,
                day=1,
                hour=0,
                minute=0,
                second=0,
            ),
            datetime.datetime(
                year=current.year,
                month=current.month,
                day=calendar.monthrange(current.year, current.month)[1],
                hour=23,
                minute=59,
                second=59,
            ),
        )
        current = current + relativedelta(months=1)


def create_limits(order):
    result = []

    for name, value in order.limits.items():
        limit, created = models.ResourceLimit.objects.update_or_create(
            resource_name=order.resource.name,
            resource_uuid=order.resource.uuid.hex.replace('-', ''),
            project_name=order.resource.project.name,
            project_uuid=order.resource.project.uuid.hex.replace('-', ''),
            customer_name=order.resource.project.customer.name,
            customer_uuid=order.resource.project.customer.uuid.hex.replace('-', ''),
            date=order.consumer_reviewed_at.date(),
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


def resource_date_iterator(force, metric_model):
    now = datetime.datetime.now()
    print('Start: %s' % now)

    if force:
        metric_model.objects.all().delete()

    if not metric_model.objects.count():
        force = True

    resources = (
        waldur_models.Resource.objects.using('waldur')
        .exclude(limits={}, state=waldur_models.Resource.States.CREATING)
        .order_by('id', 'created')
    )

    if not force:
        terminate_resource_uuids = set(
            waldur_models.Order.objects.using('waldur')
            .filter(
                state=waldur_models.Order.States.DONE,
                type=waldur_models.Order.Types.TERMINATE,
            )
            .values_list('resource__uuid', flat=True)
        )
        resources = resources.exclude(uuid__in=terminate_resource_uuids)

    for resource in resources:
        terminated_date = None

        if force:
            terminate_order = (
                waldur_models.Order.objects.using('waldur')
                .filter(
                    resource_id=resource.id,
                    state=waldur_models.Order.States.DONE,
                    type=waldur_models.Order.Types.TERMINATE,
                )
                .first()
            )

            if terminate_order:
                terminated_date = terminate_order.consumer_reviewed_at.replace(
                    tzinfo=None
                )

        created_date = resource.created.replace(tzinfo=None)

        for start, end in date_iterator(
            created_date if force else now, terminated_date or now
        ):
            yield resource, start, end, created_date, terminated_date


def update_resource_limits(force=False):
    previous = None

    for resource, start, end, created_date, terminated_date in resource_date_iterator(
        force, models.ResourceLimit
    ):
        print(
            'Sync resource: %s, from: %s, to: %s created: %s, terminated: %s'
            % (resource.uuid.hex, start, end, created_date, terminated_date)
        )

        order = (
            waldur_models.Order.objects.using('waldur')
            .filter(
                state=waldur_models.Order.States.DONE,
                type__in=[
                    waldur_models.Order.Types.CREATE,
                    waldur_models.Order.Types.UPDATE,
                ],
                resource_id=resource.id,
                consumer_reviewed_at__gte=start,
                consumer_reviewed_at__lte=end,
            )
            .exclude(limits={})
            .order_by('-consumer_reviewed_at')
        ).first()

        if order:
            previous = create_limits(order)
        elif previous and previous[0].resource_uuid == resource.uuid.hex:
            copy_limits(previous, start)
        else:
            print(
                'Sync of resource has been skipped because order and previous order are not found. '
                'Resource %s, state %s, from %s, to %s.'
                % (resource.uuid.hex, resource.get_state_display(), start, end)
            )
            continue

    print('End: %s' % datetime.datetime.now())
