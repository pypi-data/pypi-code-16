from django.core.management.base import BaseCommand, CommandError
import django_configure


class Command(BaseCommand):
    help = 'Generates config file and wsgi file in designated location'

    def add_arguments(self, parser):
        parser.add_argument('config_path', type=str)
        parser.add_argument('wsgi_path', nargs='?', type=str)
        parser.add_argument('--dev', action='store_true')

    def handle(self, *args, **options):
        config = django_configure.main_config

        config.config_path = options['config_path']
        config_output = config.generate(dev=options['dev'])

        self.stdout.write(self.style.SUCCESS('Successfully generated "%s"' % options['config_path']))
        self.stdout.write('Config output:')
        self.stdout.write(config_output)

        if options['wsgi_path'] is not None:
            wsgi_output = config.generate_wsgi(options['wsgi_path'])
            self.stdout.write(self.style.SUCCESS('Successfully generated "%s"' % options['wsgi_path']))
            self.stdout.write('Wsgi output:')
            self.stdout.write(wsgi_output)
