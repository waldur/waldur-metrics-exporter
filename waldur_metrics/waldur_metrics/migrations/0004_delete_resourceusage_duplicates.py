# Generated by Django 3.2.20 on 2024-06-25 08:44

from django.db import migrations
from django.db.models import Count


def removing_duplicates(apps, schema_editor):
    ResourceUsage = apps.get_model("waldur_metrics", "ResourceUsage")
    duplicates = (
        ResourceUsage.objects.all()
        .values('date', 'resource_uuid', 'project_uuid', 'customer_uuid', 'type')
        .annotate(dcount=Count('date'))
        .filter(dcount__gt=1)
    ).order_by('date')

    def get_prev_value(resource_uuid, usage_type, date):
        prev = (
            ResourceUsage.objects.filter(
                resource_uuid=resource_uuid,
                type=usage_type,
                date__lt=date,
            )
            .order_by('-date')
            .first()
        )

        if not prev:
            return 0

        return prev.usage_since_creation

    for d in duplicates:
        usages = ResourceUsage.objects.filter(
            date=d['date'],
            resource_uuid=d['resource_uuid'],
            project_uuid=d['project_uuid'],
            customer_uuid=d['customer_uuid'],
            type=d['type'],
        )
        first = usages.first()
        usages.exclude(id=first.id).delete()
        first.usage_since_creation = (
            get_prev_value(first.resource_uuid, first.type, first.date) + first.usage
        )
        first.save()


class Migration(migrations.Migration):

    dependencies = [
        ('waldur_metrics', '0003_resourcelimit_resourceusage'),
    ]

    operations = [
        migrations.RunPython(removing_duplicates),
    ]