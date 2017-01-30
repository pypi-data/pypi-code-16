from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = "nimble/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = 'Dashboard Test'
        return context
