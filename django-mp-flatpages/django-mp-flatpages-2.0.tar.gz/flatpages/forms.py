
from django import forms
from django.conf import settings
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from flatpages.models import FlatPage


class FlatpageForm(forms.ModelForm):

    url = forms.RegexField(
        label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
        help_text=_("Example: '/about/contact/'. Make sure to have leading"
                    " and trailing slashes."),
        error_messages={
            "invalid": _("This value must contain only letters, numbers,"
                         " dots, underscores, dashes, slashes or tildes."),
        },
    )

    def __init__(self, *args, **kwargs):

        if apps.is_installed('ckeditor_uploader'):
            from ckeditor_uploader.widgets import CKEditorUploadingWidget
            self.fields['content'].widget = CKEditorUploadingWidget

        elif apps.is_installed('ckeditor'):
            from ckeditor.widgets import CKEditorWidget
            self.fields['content'].widget = CKEditorWidget

        super(FlatpageForm, self).__init__(*args, **kwargs)

    def clean_url(self):
        url = self.cleaned_data['url']

        if not url.startswith('/'):
            raise forms.ValidationError(
                _("URL is missing a leading slash."))

        if (settings.APPEND_SLASH and
                'django.middleware.common.CommonMiddleware' in
                    settings.MIDDLEWARE_CLASSES and not url.endswith('/')):
            raise forms.ValidationError(
                _("URL is missing a trailing slash."))

        return url

    class Meta:
        model = FlatPage
        fields = '__all__'
