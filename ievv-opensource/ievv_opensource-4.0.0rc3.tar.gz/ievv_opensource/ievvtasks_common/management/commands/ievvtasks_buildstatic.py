from django.conf import settings
from django.core.management.base import BaseCommand
from ievv_opensource.utils.logmixin import Logger


class Command(BaseCommand):
    help = 'A build system (for sass, javascript, ...).'

    def add_arguments(self, parser):
        parser.add_argument('-w', '--watch', dest='watch',
                            required=False, action='store_true',
                            help='Starts a blocking process that watches for changes.')
        parser.add_argument('-a', '--appname', dest='appnames',
                            required=False, default=[], action='append',
                            help='Specify one or more apps to build. If not specified, all '
                                 'apps are built. Example: "-a ievv_jsbase -a demoapp2"')
        parser.add_argument('-s', '--skip', dest='skipgroups',
                            required=False, action='append',
                            help='Skip a plugin group. Can be repeated. Example: "-s test -s css".')
        parser.add_argument('--skip-js', dest='skipgroups',
                            required=False, action='append_const', const='js',
                            help='Skip building javascript. The same as "--skip js".')
        parser.add_argument('--skip-css', dest='skipgroups',
                            required=False, action='append_const', const='css',
                            help='Skip building css. The same as "--skip css".')
        parser.add_argument('--skip-jstests', dest='skipgroups',
                            required=False, action='append_const', const='jstest',
                            help='Skip running javascript tests. The same as "--skip jstest".')
        parser.add_argument('--skip-slow-tests', dest='skipgroups',
                            required=False, action='append_const', const='slow-jstest',
                            help='Skip running slow javascript tests. The same as "--skip slow-jstest". '
                                 'Slow javascript tests are also skipped if you use "--skip-jstests".')
        parser.add_argument('--loglevel', dest='loglevel',
                            required=False, default='stdout',
                            choices=['debug', 'stdout', 'info', 'warning', 'error'],
                            help='Set loglevel. Can be one of: debug, stdout, info, warning or error '
                                 '(listed in order of verbosity).')
        parser.add_argument('-q', '--quiet', dest='loglevel',
                            required=False, action='store_const', const='warning',
                            help='Quiet output. Same as "--loglevel warning".')
        parser.add_argument('--production', dest='production_mode',
                            required=False, action='store_true', default=False,
                            help='Build in production mode.')
        parser.add_argument('--debug', dest='loglevel',
                            required=False, action='store_const', const='debug',
                            help='Verbose output. Same as "--loglevel debug".')

    def handle(self, *args, **options):
        loglevel = getattr(Logger, options['loglevel'].upper())
        appnames = options['appnames']
        skipgroups = options['skipgroups']
        production_mode = options['production_mode']
        skipgroups = set(skipgroups or [])
        if 'skip-jstests' in skipgroups:
            skipgroups.add('skip-slow-jstests')
        if 'skip-js' in skipgroups:
            skipgroups.add('skip-slow-jstests')
            skipgroups.add('skip-jstests')
        if appnames:
            try:
                settings.IEVVTASKS_BUILDSTATIC_APPS.validate_appnames(appnames=appnames)
            except ValueError as error:
                self.stderr.write(str(error))
                raise SystemExit()
        settings.IEVVTASKS_BUILDSTATIC_APPS.configure_logging(
            loglevel=loglevel,
            command_error_message='Re-run with "--debug" for more details.')
        if production_mode:
            settings.IEVVTASKS_BUILDSTATIC_APPS.set_production_mode()
        else:
            settings.IEVVTASKS_BUILDSTATIC_APPS.set_development_mode()
        settings.IEVVTASKS_BUILDSTATIC_APPS.log_help_header()
        settings.IEVVTASKS_BUILDSTATIC_APPS.install(appnames=appnames, skipgroups=skipgroups)
        settings.IEVVTASKS_BUILDSTATIC_APPS.run(appnames=appnames, skipgroups=skipgroups)
        if options['watch']:
            settings.IEVVTASKS_BUILDSTATIC_APPS.watch(appnames=appnames, skipgroups=skipgroups)
