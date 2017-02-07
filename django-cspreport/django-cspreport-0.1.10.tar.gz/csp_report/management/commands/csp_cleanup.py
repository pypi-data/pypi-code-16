from datetime import timedelta, datetime

from django.core.management import BaseCommand
from csp_report.models import CSPReport


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--max_age',
            default=7,
            type=int,
            help='Number of days to store data',
        )

    def handle(self, *args, **options):
        max_age = options.get('max_age')
        if max_age:
            reports = CSPReport.objects.filter(date__lte=datetime.now()-timedelta(days=max_age))
            print('Trying to remove {} reports'.format(len(reports)))
            reports.delete()
