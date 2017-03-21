
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from accounts.forms import UserChangeForm, ConfirmPasswordForm


@method_decorator(login_required, "dispatch")
class ProfileUpdateView(FormView):

    form_class = UserChangeForm
    success_url = reverse_lazy('accounts:profile')
    template_name = 'account/profile/change.html'

    def get_form_kwargs(self):
        kwargs = super(ProfileUpdateView, self).get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Profile successfully changed'))
        return super(ProfileUpdateView, self).form_valid(form)


@method_decorator(login_required, "dispatch")
class RemoveProfileView(FormView):

    form_class = ConfirmPasswordForm
    success_url = reverse_lazy('home')
    template_name = 'account/profile/remove.html'
    fields = ['password']

    def get_form_kwargs(self):
        kwargs = super(RemoveProfileView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.is_active = False
        user.save()

        logout(self.request)

        messages.success(self.request, _('Profile successfully removed'))
        return super(RemoveProfileView, self).form_valid(form)
