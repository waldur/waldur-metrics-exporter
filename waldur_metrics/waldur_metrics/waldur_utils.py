import calendar
import datetime

from django.utils import timezone


def month_start(date):
    return timezone.make_aware(
        datetime.datetime(day=1, month=date.month, year=date.year)
    )


def month_end(date):
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    last_day_of_month = datetime.date(
        month=date.month, year=date.year, day=days_in_month
    )
    last_second_of_month = datetime.datetime.combine(
        last_day_of_month, datetime.time.max
    )
    return timezone.make_aware(last_second_of_month, timezone.get_current_timezone())
