from django import forms
from photologue.models import Photo
from django.conf import settings

MULTISITE = getattr(settings, 'PHOTOLOGUE_MULTISITE', False)


class PhotoAdminExtendedForm(forms.ModelForm):

    class Meta:
        model = Photo
        if MULTISITE:
            exclude = []
        else:
            exclude = ['sites', 'caption']
