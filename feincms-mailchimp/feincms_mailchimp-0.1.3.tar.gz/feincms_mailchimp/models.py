from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


LANGUAGES = settings.LANGUAGES


class MailchimpFormContent(models.Model):

    class Meta:
        abstract = True
        verbose_name = "Mailchimp Form"
        verbose_name_plural = "Mailchimp Forms"

    post_url = models.CharField(
        _('POST URL'),
        max_length=2100,
        null=True)

    user_id = models.CharField(
        _('User ID'),
        max_length=32,
        null=True)

    list_id = models.CharField(
        _('List ID'),
        max_length=32,
        null=True)

    placeholder = models.CharField(
        _('Placeholder'),
        max_length=50,
        blank=True, null=True)

    description = models.TextField(
        _('Description'),
        blank=True, null=True)

    def process(self, request, **kwargs):
        if request.method == 'GET':
            self.email = request.GET.get('email')

        email = getattr(self, 'email', '')
        template_vars = {
            'post_url': self.post_url,
            'user_id': self.user_id,
            'list_id': self.list_id,
            'description': self.description,
            'placeholder': self.placeholder,
            'form_id': id(self),
            'email': email,
        }

        self.rendered_output = render_to_string(
            'feincms_mailchimp/signup.html',
            template_vars
        )

    def render(self, **kwargs):
        return getattr(self, 'rendered_output', '')
