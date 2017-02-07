from __future__ import unicode_literals

from django.views.generic import FormView as DjangoFormView

from common.generics import (
    ExtraContextMixin, RedirectionMixin, ViewPermissionCheckMixin
)

try:
    from common.generics import MultipleObjectFormActionView
except ImportError:
    from .mixins import (
        FormExtraKwargsMixin, MultipleObjectMixin, ObjectActionMixin
    )

    class MultipleObjectFormActionView(ObjectActionMixin, MultipleObjectMixin, FormExtraKwargsMixin, ViewPermissionCheckMixin, ExtraContextMixin, RedirectionMixin, DjangoFormView):
        """
        This view will present a form and upon receiving a POST request will
        perform an action on an object or queryset
        """

        template_name = 'appearance/generic_form.html'

        def form_valid(self, form):
            self.view_action(form=form)
            return super(MultipleObjectFormActionView, self).form_valid(form=form)
