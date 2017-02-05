""" Replace the existing user class with our own in the admin """
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import (
    UserChangeForm as BaseUserChangeForm,
    UserCreationForm as BaseUserCreationForm)
from django.utils.translation import ugettext_lazy as _


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = get_user_model()
        fields = '__all__'


class UserCreationForm(BaseUserCreationForm):
    """Form that creates a user with no privileges from an email and password."""
    error_messages = {
        'password_mismatch': _(""),
        'duplicate_email': _("A user with that email already exists"),
    }

    class Meta:
        model = get_user_model()
        fields = ['email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "The two password fields didn't match.", code='password_mismatch')
        if password_validation is not None:
            password_validation.validate_password(password2, self.instance)
        return password2


class UserAdmin(BaseUserAdmin):
    """ The admin interface for the user model """
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('date_joined', 'last_login',)}),
    )
    add_fieldsets = ((
        None,
        {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }
    ),)

    list_display = ('email', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ['date_joined']
