from django.forms import ModelForm
from nimble.models.profile import Profile


class ProfileForm(ModelForm):

    class Meta:
        model = Profile
        fields = ['theme']
