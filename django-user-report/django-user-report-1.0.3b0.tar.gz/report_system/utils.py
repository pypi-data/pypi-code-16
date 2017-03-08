from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist
from report_system.conf import settings
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
import logging
logger = logging.getLogger(__name__)


def render_mail(template_prefix, email, context):
    """
    Renders an e-mail to `email`.  `template_prefix` identifies the
    e-mail that is to be sent, e.g. "account/email/email_confirmation"
    """
    subject = render_to_string('{0}_subject.txt'.format(template_prefix), context)
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    subject = force_text(subject)

    bodies = {}
    for ext in ['html', 'txt']:
        try:
            template_name = '{0}_message.{1}'.format(template_prefix, ext)
            bodies[ext] = render_to_string(template_name,
                                           context).strip()
        except TemplateDoesNotExist:
            if ext == 'txt' and not bodies:
                # We need at least one body
                raise
    if 'txt' in bodies:
        msg = EmailMultiAlternatives(subject,
                                     bodies['txt'],
                                     settings.REPORT_EMAIL_FROM,
                                     [email])
        if 'html' in bodies:
            msg.attach_alternative(bodies['html'], 'text/html')
    else:
        msg = EmailMessage(subject,
                           bodies['html'],
                           settings.DEFAULT_FROM_EMAIL,
                           [email])
        msg.content_subtype = 'html'  # Main content is now text/html
    return msg


def send_mail(template_prefix, email, context):
    msg = render_mail(template_prefix, email, context)
    msg.send()


def get_email_receiver(target_object):
    object_name = "{0}.{1}".format(target_object._meta.app_label, target_object._meta.object_name)
    if object_name in settings.REPORT_EMAIL_RECEIVER_FIELDNAME:
        field_name = settings.REPORT_EMAIL_RECEIVER_FIELDNAME[object_name]
        if field_name is None:
            return target_object
        else:
            return getattr(target_object, field_name)