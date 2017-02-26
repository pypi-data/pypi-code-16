from django.core.management.base import BaseCommand, CommandError
import os
import shutil
import platform

from ._tools import get_p4a_args, update_apk, parcefiles, overwrite_p4a, post_update_apk, read_configuration

class Command(BaseCommand):
    help = 'Generate .apk for debug'
    can_import_settings = True

    #----------------------------------------------------------------------
    def add_arguments(self, parser):
        """"""

        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            default=True,
            help='Debug apk with',
        )

        parser.add_argument(
            '--release',
            action='store_true',
            dest='release',
            default=False,
            help='Release unsigned apk',
        )

        parser.add_argument(
            '--install',
            action='store_true',
            dest='install',
            default=False,
            help='Install apk with adb.',
        )

        parser.add_argument(
            '--run',
            action='store_true',
            dest='run',
            default=False,
            help='Run apk with adb.',
        )

        parser.add_argument(
            '--logcat',
            action='store_true',
            dest='logcat',
            default=False,
            help='Log apk with adb.',
        )



    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings

        update_apk(settings)
        overwrite_p4a(settings)

        NAME = os.path.split(settings.BASE_DIR)[-1]
        build_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME)
        name = settings.ANDROID['APK']['name']
        version = settings.ANDROID['APK']['version']
        apk_debug = os.path.join(build_dir, '{}-{}-debug.apk'.format(name, version)).replace(' ', '')
        apk_release = os.path.join(build_dir, '{}-{}-release.apk'.format(name, version)).replace(' ', '')
        package = settings.ANDROID['APK']['package']

        #collectstatic
        app_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME, 'app')
        os.chdir(os.path.join(app_dir, NAME))
        host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        os.system('{} manage.py collectstatic --noinput'.format(host_python ))

        post_update_apk(settings)

        os.chdir(build_dir)
        argv = read_configuration(settings)

        if options['release']:
            if os.path.exists(apk_release):
                os.remove(apk_release)

            os.environ['P4A_RELEASE_KEYSTORE'] = settings.ANDROID['KEY']['RELEASE_KEYSTORE']
            os.environ['P4A_RELEASE_KEYALIAS'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS']
            os.environ['P4A_RELEASE_KEYSTORE_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYSTORE_PASSWD']
            os.environ['P4A_RELEASE_KEYALIAS_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS_PASSWD']

            self.p4a_sign(settings, argv, apk_release)
            #self.manual_sign(settings, argv, apk_debug, apk_release)
            run_apk = apk_release


        elif options['debug']:
            if os.path.exists(apk_debug):
                os.remove(apk_debug)

            #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
            os.system('p4a apk {}'.format(argv))
            shutil.copy(apk_debug, settings.BASE_DIR)
            run_apk = apk_debug


        if options['install']:
            os.system("adb start-server")
            os.system("adb install -r {}".format(apk_release))

            if options['run']:
                os.system("adb shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1".format(PACKAGE=package))

            if options['logcat']:
                os.system("adb logcat")


    #----------------------------------------------------------------------
    def p4a_sign(self, settings, argv, apk_release):
        """"""
        #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        os.system('p4a apk --release {}'.format(argv))
        shutil.copy(apk_release, settings.BASE_DIR)


    #----------------------------------------------------------------------
    def manual_sign(self, settings, argv, apk_debug, apk_release):
        """"""
        if not os.path.exists(apk_debug):
            #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
            os.system('p4a apk {}'.format(argv))

        apk_unaligned = apk_debug.replace("-debug.apk", "-unaligned.apk")
        shutil.copy(apk_debug, apk_unaligned)

        v = os.listdir(os.path.join(settings.ANDROID['ANDROID']['SDK'], 'build-tools'))
        v.sort()
        zipalign = os.path.join(settings.ANDROID['ANDROID']['SDK'], 'build-tools', v[-1], 'zipalign')

        os.system("jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -storepass {} -keypass {} -keystore {} {} {}".format(os.getenv('P4A_RELEASE_KEYSTORE_PASSWD'), os.getenv('P4A_RELEASE_KEYALIAS_PASSWD'), os.getenv('P4A_RELEASE_KEYSTORE'), apk_unaligned, os.getenv('P4A_RELEASE_KEYALIAS')))
        os.system("jarsigner -verify -verbose -certs {}".format(apk_unaligned))
        os.system("{} -v 4 {} {}".format(zipalign, apk_unaligned, apk_release))
        shutil.copy(apk_release, settings.BASE_DIR)
