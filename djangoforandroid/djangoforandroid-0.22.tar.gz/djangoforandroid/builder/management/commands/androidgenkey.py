from django.core.management.base import BaseCommand, CommandError
import os
import shutil

class Command(BaseCommand):
    help = 'Generate .apk for debug'
    can_import_settings = True


    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings

        store = settings.ANDROID['KEY']['RELEASE_KEYSTORE']
        alias = settings.ANDROID['KEY']['RELEASE_KEYALIAS']
        os.chdir(settings.BASE_DIR)
        os.system("keytool -genkey -v -keystore {} -alias {} -keyalg RSA -keysize 2048 -validity 10000".format(store, alias))
