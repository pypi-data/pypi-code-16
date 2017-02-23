
from django.db import models
from django.utils.translation import ugettext_lazy as _


class FlatPage(models.Model):

    url = models.CharField(_('URL'), max_length=100, db_index=True)

    title = models.CharField(_('title'), max_length=200)

    meta_k = models.CharField(_('keywords'), max_length=200)

    meta_d = models.CharField(_('description'), max_length=200)

    content = models.TextField(_('content'), blank=True)

    template_name = models.CharField(
        _('template name'), max_length=70, blank=True,
        help_text=_(
            "Example: 'flatpages/contact_page.html'. If this isn't provided, "
            "the system will use 'flatpages/default.html'."
        ),
    )
    registration_required = models.BooleanField(
        _('registration required'),
        help_text=_("If this is checked, only logged-in "
                    "users will be able to view the page."),
        default=False)

    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('url',)

    def __unicode__(self):
        return "%s -- %s" % (self.url, self.title)
