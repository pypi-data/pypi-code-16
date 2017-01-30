from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy

from django.views.generic import ListView
from nimble.models.story import Story


class StoryList(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('login')

    model = Story
    queryset = Story.objects.order_by('id')
