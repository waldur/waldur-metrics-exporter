from django.core.management.base import BaseCommand

from waldur_metrics import utils


class Command(BaseCommand):
    help = "Update aggregated limit metrics."

    def add_arguments(self, parser):
        parser.add_argument(
            '-d',
            '--deep',
            dest='deep',
            action='store_true',
            help='Deep update. All old metrics will be deleted and imported again.',
        )
        parser.add_argument('-y', '--year', dest='year', type=int)
        parser.add_argument('-t', '--component_type', dest='component_type')
        parser.add_argument('-c', '--country', dest='country')

    def handle(
        self, deep=False, year=None, country=None, component_type=None, *args, **options
    ):
        utils.update_limits(deep, year, country, component_type)
