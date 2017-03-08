from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from report_system.conf import settings
from django.utils.translation import ugettext_lazy as _
from report_system.managers import TicketManager
# Create your models here.


class TicketType(models.Model):
    title = models.TextField(_('Title'))
    related_model = models.CharField(max_length=20, choices=settings.REPORT_SLUG_MODEL_MAPPINGS)

    def __str__(self):
        return "%s..." % (self.title[:50])

    class Meta:
        db_table = "report_tickettypes"
        permissions = [("can_write", "Can rwx types")]
        verbose_name = _('type')
        verbose_name_plural = _('types')


class Ticket(models.Model):

    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    # Metadata about the comment
    site = models.ForeignKey(Site)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'), related_name="%(class)s_tickets")
    comment = models.TextField(_('Extra description'), max_length=settings.REPORT_COMMENT_MAX_LENGTH, blank=True)
    submit_date = models.DateTimeField(_('date/time submitted'), auto_now_add=True)
    is_closed = models.BooleanField(_('is removed'), default=False,
                                    help_text=_('Check this box if the ticket is closed.'))
    types = models.ManyToManyField(TicketType, related_name='tickets', related_query_name='ticket')
    version = models.CharField(_("program version"), max_length=50, blank=True)
    waiting = 'WR'
    CLOSE = 'CL'
    in_progress = 'IP'
    STATUS_CHOICE = (
        (waiting, 'Waiting For Review'),
        (CLOSE, 'Closed'),
        (in_progress, 'In Progress'),
    )
    UNREAD = 'UR'
    HIGH_PRIORITY = 'HP'
    COMPLETED_AND_DELETE = 'CD'
    COMPLETED_AND_INACTIVATE = 'CI'
    COMPLETED_AND_ACTIVATE = 'CA'
    BACKEND_STATUS_CHOICE = (
        (UNREAD, 'Unread'),
        (HIGH_PRIORITY, 'High Priority Unread'),
        (CLOSE, 'Closed Ticket'),
        (COMPLETED_AND_DELETE, 'Complete Review and Delete Target'),
        (COMPLETED_AND_INACTIVATE, 'Complete Review and Inactivate Target'),
        (COMPLETED_AND_ACTIVATE, 'Complete Review and Activate Target'),
    )
    frontend_status = models.CharField(max_length=2, choices=STATUS_CHOICE, default=waiting)
    backend_status = models.CharField(max_length=2, choices=BACKEND_STATUS_CHOICE, default=UNREAD)
    # Manager
    objects = TicketManager()

    class Meta:
        db_table = "report_tickets"
        ordering = ('submit_date',)
        permissions = [("can_review", "Can review tickets")]
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')

    @property
    def ticket_no(self):
        tid = self.id
        model_name = self.content_type.model
        return "#%s-%s" % (model_name, tid)

    @property
    def user_info(self):
        u = self.user
        email = ""
        if u.email:
            email = u.email
        return "@%s(%s)" % (u.username, email)

    @property
    def user_email(self):
        u = self.user
        email = ""
        if u.email:
            email = u.email
        return email

    def __str__(self):
        return "%s: %s..." % (self.user, self.comment[:50])

