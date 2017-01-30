from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import Http404, HttpResponseForbidden
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

from nimble.forms.debt import DebtForm
from nimble.forms.feature import FeatureForm
from nimble.models.debt import Debt
from nimble.models.feature import Feature
from nimble.models.story import Story

form_mapping = {
    Debt: DebtForm,
    Feature: FeatureForm,
}


class StoryDisplay(DetailView):
    model = Story
    reverse_url = 'story_detail'
    template_name = 'nimble/story_detail.html'

    def get(self, *args, **kwargs):
        self.ident = kwargs.get('ident')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        if self.ident != story.ident:
            raise Http404("Object does not exist")
        form = form_mapping[type(story)]
        context['form'] = form(instance=story)
        context['active_tab'] = 'details'
        return context


class StoryPost(SingleObjectMixin, FormView):
    template_name = 'nimble/story_detail.html'
    model = Story
    reverse_url = 'story_detail'

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:  # pragma: no cover
            return HttpResponseForbidden()
        self.object = self.get_object()
        self.form_class = form_mapping[type(self.object)]
        form = self.form_class(request.POST)
        if form.is_valid():
            self.object.update(request.user, form.cleaned_data)
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(self.reverse_url, kwargs={
            'pk': self.object.pk, 'ident': self.object.ident
        })


class StoryDetail(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        view = StoryDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = StoryPost.as_view()
        return view(request, *args, **kwargs)
