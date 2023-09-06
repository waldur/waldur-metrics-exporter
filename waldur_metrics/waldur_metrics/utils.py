import datetime
import os

from django.db.models import Sum

from waldur_metrics import models, waldur_models, waldur_utils

START_YEAR = int(os.environ.get('START_YEAR', '2020'))


def date_iterator(start_year=0, start_month=0):
    current_year = datetime.date.today().year
    current_month = datetime.date.today().month

    for year in range(max(START_YEAR, start_year), current_year + 1):
        for month in range(1, 12 + 1):
            if year == start_year and month < start_month:
                continue

            if year == current_year and month > current_month:
                break

            start = waldur_utils.month_start(
                datetime.datetime(day=1, month=month, year=year)
            )
            end = waldur_utils.month_end(
                datetime.datetime(day=1, month=month, year=year)
            )
            yield start, end


def _init_func(klass, deep, country, component_type):
    if deep:
        klass.objects.all().delete()

    if country:
        countries = [country]
    else:
        countries = (
            waldur_models.Customer.objects.using('waldur')
            .exclude(country='')
            .order_by('country')
            .values_list('country', flat=True)
            .distinct()
        )

    if component_type:
        component_types = [component_type]
    else:
        component_types = (
            waldur_models.OfferingComponent.objects.using('waldur')
            .all()
            .order_by()
            .values_list('type', flat=True)
            .distinct()
        )

    return countries, component_types


def update_country_usage(deep=False, year=None, country=None, component_type=None):
    countries, component_types = _init_func(
        models.AggregatedCountryUsageMetric, deep, country, component_type
    )

    for country in countries:
        for component_type in component_types:

            start_year = 0
            start_month = 0

            if year:
                start_year = year
            else:
                last_metric = (
                    models.AggregatedCountryUsageMetric.objects.filter(
                        country=country,
                        component_type=component_type,
                    )
                    .order_by('-date')
                    .first()
                )

                if last_metric:
                    start_year = last_metric.date.year
                    start_month = last_metric.date.month

            for start, end in date_iterator(start_year, start_month):
                usages = (
                    waldur_models.ComponentUsage.objects.using('waldur')
                    .filter(
                        component__type=component_type,
                        resource__project__customer__country=country,
                        date__gte=start,
                        date__lte=end,
                    )
                    .aggregate(Sum('usage'))['usage__sum']
                    or 0
                )
                print(
                    ",".join(
                        [
                            f'{str(start.year)}-{str(start.month)}',
                            country,
                            component_type,
                            str(usages),
                        ]
                    )
                )

                prev_usage_during_month = (
                    models.AggregatedCountryUsageMetric.objects.filter(
                        country=country,
                        component_type=component_type,
                        date__lt=start,
                        date__gte=datetime.date(year=start.year, month=1, day=1),
                    ).aggregate(Sum('usage_during_month'))['usage_during_month__sum']
                    or 0
                )

                models.AggregatedCountryUsageMetric.objects.update_or_create(
                    date=start,
                    country=country,
                    component_type=component_type,
                    usage_during_month=usages,
                    usage_since_beginning_of_year=usages + prev_usage_during_month,
                )


def get_grow_limit(limit, item):
    prev_items = (
        waldur_models.OrderItem.objects.using('waldur')
        .filter(
            resource=item.resource,
            state=waldur_models.OrderItem.States.DONE,
            type__in=[
                waldur_models.OrderItem.Types.CREATE,
                waldur_models.OrderItem.Types.UPDATE,
            ],
            created__lt=item.created,
        )
        .exclude(id=item.id)
        .order_by('-created')
    )
    limit_value = item.limits.get(limit)

    for p in prev_items:
        prev_value = p.limits.get(limit)

        if prev_value is not None:

            if limit_value > prev_value:
                return limit_value - prev_value
            else:
                return 0
    return 0


def update_country_limits(deep=False, year=None, country=None, component_type=None):
    countries, component_types = _init_func(
        models.AggregatedCountryLimitMetric, deep, country, component_type
    )

    for country in countries:

        start_year = 0
        start_month = 0

        if year:
            start_year = year
        else:
            last_metric = (
                models.AggregatedCountryLimitMetric.objects.filter(
                    country=country,
                )
                .order_by('-date')
                .first()
            )

            if last_metric:
                start_year = last_metric.date.year
                start_month = last_metric.date.month

        for start, end in date_iterator(start_year, start_month):
            new_resources = waldur_models.Resource.objects.using('waldur').filter(
                project__customer__country=country,
                created__gte=start,
                created__lte=end,
            )
            old_resources = waldur_models.Resource.objects.using('waldur').filter(
                project__customer__country=country,
                created__lt=start,
            )
            order_items = waldur_models.OrderItem.objects.using('waldur').filter(
                resource__in=old_resources,
                created__gte=start,
                created__lte=end,
                state=waldur_models.OrderItem.States.DONE,
                type=waldur_models.OrderItem.Types.UPDATE,
            )

            for limit in component_types:
                limit_value_sum = 0

                # add new limits
                for resource in new_resources:
                    limit_value = resource.limits.get(limit)

                    if limit_value:
                        limit_value_sum += limit_value

                # grow old limits
                for item in order_items:
                    limit_value = item.limits.get(limit)

                    if not limit_value:
                        continue

                    grow_limit = get_grow_limit(limit, item)
                    limit_value_sum += grow_limit

                print(
                    ",".join(
                        [
                            f'{str(start.year)}-{str(start.month)}',
                            country,
                            limit,
                            str(limit_value_sum),
                        ]
                    )
                )

                prev_usage_during_month = (
                    models.AggregatedCountryLimitMetric.objects.filter(
                        country=country,
                        component_type=limit,
                        date__lt=start,
                        date__gte=datetime.date(year=start.year, month=1, day=1),
                    ).aggregate(Sum('usage_during_month'))['usage_during_month__sum']
                    or 0
                )

                models.AggregatedCountryLimitMetric.objects.update_or_create(
                    date=start,
                    country=country,
                    component_type=limit,
                    usage_during_month=limit_value_sum,
                    usage_since_beginning_of_year=limit_value_sum
                    + prev_usage_during_month,
                )
