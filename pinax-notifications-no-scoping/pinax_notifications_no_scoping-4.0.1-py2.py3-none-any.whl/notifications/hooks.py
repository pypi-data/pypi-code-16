import base64

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet
from django.utils.six.moves import cPickle as pickle

from .conf import settings
from .utils import load_media_defaults


class DefaultHookSet(object):

    def notice_setting_for_user(self, user, notice_type, medium):
        kwargs = {
            "notice_type": notice_type,
            "medium": medium
        }
        try:
            return user.noticesetting_set.get(**kwargs)
        except ObjectDoesNotExist:
            _, NOTICE_MEDIA_DEFAULTS = load_media_defaults()
            default = (NOTICE_MEDIA_DEFAULTS[medium] <= notice_type.default)
            kwargs.update({"send": default})
            setting = user.noticesetting_set.create(**kwargs)
            return setting

    def queue(self, users, label, extra_context=None, sender=None):
        """
        Queue the notification in NoticeQueueBatch. This allows for large amounts
        of user notifications to be deferred to a seperate process running outside
        the webserver.
        """
        from pinax.notifications.models import NoticeQueueBatch
        if extra_context is None:
            extra_context = {}
        if isinstance(users, QuerySet):
            users = [row["pk"] for row in users.values("pk")]
        else:
            users = [user.pk for user in users]
        notices = []
        for user in users:
            notices.append((user, label, extra_context, sender))
        NoticeQueueBatch(pickled_data=base64.b64encode(pickle.dumps(notices))).save()


class HookProxy(object):

    def __getattr__(self, attr):
        return getattr(settings.PINAX_NOTIFICATIONS_HOOKSET, attr)


hookset = HookProxy()
