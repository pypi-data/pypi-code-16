from appconf import AppConf
from django.conf import settings


class ReportSystemConf(AppConf):
    COMMENT_MAX_LENGTH = 3000
    SLUG_MODEL_MAPPINGS = (
        ('user', settings.AUTH_USER_MODEL)
    )
    EMAIL_RECEIVER_FIELDNAME = {
        settings.AUTH_USER_MODEL: None
    }
    HIGH_PRIORITY_TICKETS_NUM = 5
    EMAIL_FROM = settings.EMAIL_HOST_USER

    class Meta:
        prefix = 'report'
