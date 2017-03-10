from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text


class TicketManager(models.Manager):

    def get_queryset(self):
        return super(TicketManager, self).get_queryset()

    def all_open_tickets(self):
        """
        QuerySet for all comments currently in the moderation queue.
        """
        return self.get_queryset().filter(is_closed=False)

    def for_model(self, model):
        """
        QuerySet for all comments for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_text(model._get_pk_val()))
        return qs
