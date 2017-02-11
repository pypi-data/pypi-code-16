# coding: utf-8
import hues

from django.core.management.base import BaseCommand

from elasticsearch import exceptions
from elasticsearch_dsl.connections import connections
from elasticsearch_flex.indexes import registered_indices


class Command(BaseCommand):
    help = 'Sync search indices, templates, and scripts.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete existing index',
        )

    def handle(self, delete, *args, **options):
        indices = registered_indices()
        connection = connections.get_connection()
        hues.info('Using connection', connection)
        if len(indices):
            hues.info('Discovered', len(indices), 'Indexes')
        else:
            hues.warn('No search index found')
        for i, index in enumerate(indices, 1):
            hues.info('==> Initializing', index.__name__)

            index_name = index._doc_type.index
            try:
                connection.indices.close(index_name)
                if delete:
                    hues.warn('Deleting existing index.')
                    connection.indices.delete(index_name)
            except exceptions.NotFoundError:
                pass
            index.init()
            connection.indices.open(index_name)

            hues.success('--> Done {0}/{1}'.format(i, len(indices)))
