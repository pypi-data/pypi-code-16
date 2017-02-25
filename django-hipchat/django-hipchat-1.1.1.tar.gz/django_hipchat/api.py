import urllib

from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string
from django.utils.module_loading import import_string

from . import app_settings

backend_fn = import_string(app_settings.BACKEND)

def hipchat_message(template, context=None, fail_silently=app_settings.FAIL_SILENTLY):
    context = Context(context or {})

    context['settings'] = settings

    def render(component):
        return render_to_string(template, dict(
            context.flatten(),
            django_hipchat='django_hipchat/%s' % component,
        )).strip().encode('utf8', 'ignore')

    data = {
        'from': app_settings.MESSAGE_FROM,
        'color': 'yellow',
        'message': '',
        'room_id': app_settings.MESSAGE_ROOM,
        'auth_token': app_settings.AUTH_TOKEN,
        'message_format': 'html',
    }

    for part in ('auth_token', 'room_id', 'message', 'color', 'from'):
        try:
            txt = render(part)
        except Exception:
            if fail_silently:
                return
            raise

        if txt:
            data[part] = txt

    for x in ('auth_token', 'from', 'message', 'room_id'):
        if data[x]:
            continue

        if fail_silently:
            return

        assert False, "Missing or empty required parameter: %s" % x

    backend_fn('%s?%s' % (
        'https://api.hipchat.com/v1/rooms/message',
        urllib.urlencode(data),
    ), data, fail_silently)
