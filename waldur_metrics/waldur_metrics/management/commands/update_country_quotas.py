from django.core.management.base import BaseCommand

from waldur_metrics import utils


class Command(BaseCommand):
    help = "Update aggregated country quotas metrics."

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--force',
            dest='force',
            action='store_true',
            help='All old metrics will be deleted and imported again.',
        )

    def handle(self, force=False, *args, **options):
        utils.update_country_quotas(force)
