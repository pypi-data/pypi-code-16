from django.contrib.sites.models import Site
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from report_system.models import Ticket
from report_system.signals import signals
from report_system.utils import send_mail, get_email_receiver


import logging



logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ticket)
def ticket_process_routine(sender, instance, **kwargs):
    email = instance.user_email
    target = instance.content_object
    target_user = get_email_receiver(target)
    default_email_prefix = 'report_system/email/report_notice'
    context = {
        "user": target_user,
        "site": Site.objects.get_current(),
    }
    if instance.is_closed and target:
        if instance.backend_status == instance.COMPLETED_AND_INACTIVATE:
            target.is_active = False
            target.save()
            signals.target_was_inactivated.send(
                sender=Ticket,
                target=target
            )
        elif instance.backend_status == instance.COMPLETED_AND_ACTIVATE:
            target.is_active = True
            target.save()
        elif instance.backend_status == instance.COMPLETED_AND_DELETE and not isinstance(target, get_user_model()):
            name = str(target)
            extra_context = {
                "message": '"%s" you created was removed due to people report, please follow our policy and Terms condition.' %
                name,
            }
            target.delete()
        send_mail(default_email_prefix, target_user.email, context)
    else:
        pass



