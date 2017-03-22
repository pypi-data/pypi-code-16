from django.utils import timezone
import pytz


class TimezoneMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated():
            timezone.activate(pytz.timezone(request.user.timezone))
        else:
            timezone.deactivate()