
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from accounts.models import UserProfile


class UserChangeForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

        profile = getattr(self.instance, 'profile', None)

        mobile = profile.mobile if profile is not None else ''
        address = profile.address if profile is not None else ''

        self.fields['mobile'] = forms.CharField(
            label=_("Mobile"), required=False, initial=mobile)

        self.fields['address'] = forms.CharField(
            label=_("Address"), required=False, initial=address)

    def save(self, commit=True):

        user = super(UserChangeForm, self).save()

        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user)

        profile.mobile = self.cleaned_data.get('mobile', '')
        profile.address = self.cleaned_data.get('address', '')
        profile.save()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', )


class ConfirmPasswordForm(forms.Form):

    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):

        super(ConfirmPasswordForm, self).__init__(*args, **kwargs)

        self.user = user

    def clean_password(self):

        password = self.cleaned_data['password']

        if not self.user.check_password(password):
            raise forms.ValidationError(
                _("The entered password is not valid!"))

        return password
