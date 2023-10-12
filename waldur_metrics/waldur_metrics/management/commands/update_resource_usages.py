from django.core.management.base import BaseCommand

from waldur_metrics import utils_resource_usages


class Command(BaseCommand):
    help = "Update resource usages."

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            dest='force',
            action='store_true',
            help='All old metrics will be deleted and imported again.',
        )

    def handle(self, force=False, *args, **options):
        utils_resource_usages.update_resource_usages(force)
