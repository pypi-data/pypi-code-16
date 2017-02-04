# -*- coding:utf-8 -*-
from django import forms
try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import ACL


class ACLAdditionalForm(forms.ModelForm):
    acl = forms.ModelMultipleChoiceField(
        ACL.objects.all(),
        widget=admin.widgets.FilteredSelectMultiple('ACL', False),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(ACLAdditionalForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['acl'] = self.instance.acl.values_list(
                'pk', flat=True,
            )

    def save(self, *args, **kwargs):
        instance = super(ACLAdditionalForm, self).save(*args, **kwargs)

        if not instance.pk:
            instance.save()

        instance.acl = self.cleaned_data['acl']

        return instance

User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


class ACLUserAdmin(UserAdmin):
    form = ACLAdditionalForm
    fieldsets = UserAdmin.fieldsets + (
        (_('ACL'), {'fields': ('acl',)}),
    )


if getattr(settings, 'ACL_GROUP_USER_MODEL', 'auth.Group') == 'auth.Group':
    try:
        admin.site.unregister(Group)
    except admin.sites.NotRegistered:
        pass

    app_label, class_name = getattr(
        settings,
        'ACL_GROUP_USER_MODEL',
        'auth.Group',
    ).split('.')
    group_model = get_model(app_label, class_name)

    class ACLGroupAdmin(GroupAdmin):
        form = ACLAdditionalForm

    admin.site.register(Group, ACLGroupAdmin)

admin.site.register(User, ACLUserAdmin)
admin.site.register(ACL)
