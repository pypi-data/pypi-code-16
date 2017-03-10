from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Tests the Presto library"

    def handle(self, *args, **kwargs):
        print("Management command runs!")
