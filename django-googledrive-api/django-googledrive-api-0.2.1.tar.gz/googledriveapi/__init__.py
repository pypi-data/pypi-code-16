from appconf import AppConf

__version__ = '0.2.1'


class GoogleDriveAPIConf(AppConf):

    class Meta:
        prefix = 'GOOGLE_DRIVE_API'
        required = ['JSON_KEY_FILE']

    USER_EMAIL = None
    AUTO_CONVERT_MIMETYPES = []
    NUM_RETRIES = 3
