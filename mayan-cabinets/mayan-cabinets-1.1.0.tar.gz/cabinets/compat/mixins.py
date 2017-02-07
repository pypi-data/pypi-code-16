from __future__ import unicode_literals

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.utils.translation import ungettext

from .managers import filter_by_access


class FormExtraKwargsMixin(object):
    """
    Mixin that allows a view to pass extra keyword arguments to forms
    """

    form_extra_kwargs = {}

    def get_form_extra_kwargs(self):
        return self.form_extra_kwargs

    def get_form_kwargs(self):
        result = super(FormExtraKwargsMixin, self).get_form_kwargs()
        result.update(self.get_form_extra_kwargs())
        return result


class MultipleObjectMixin(object):
    """
    Mixin that allows a view to work on a single or multiple objects
    """

    model = None
    object_permission = None
    pk_list_key = 'id_list'
    pk_list_separator = ','
    pk_url_kwarg = 'pk'
    queryset = None
    slug_url_kwarg = 'slug'

    def get_pk_list(self):
        result = self.request.GET.get(
            self.pk_list_key, self.request.POST.get(self.pk_list_key)
        )

        if result:
            return result.split(self.pk_list_separator)
        else:
            return None

    def get_queryset(self):
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        pk_list = self.get_pk_list()

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        if pk_list is not None:
            queryset = queryset.filter(pk__in=self.get_pk_list())

        if pk is None and slug is None and pk_list is None:
            raise AttributeError(
                'Generic detail view %s must be called with '
                'either an object pk, a slug or an id list.'
                % self.__class__.__name__
            )

        if self.object_permission:
            return filter_by_access(
                self.object_permission, self.request.user, queryset=queryset
            )
        else:
            return queryset


class ObjectActionMixin(object):
    """
    Mixin that performs an user action to a queryset
    """

    success_message = 'Operation performed on %(count)d object'
    success_message_plural = 'Operation performed on %(count)d objects'

    def get_success_message(self, count):
        return ungettext(
            self.success_message,
            self.success_message_plural,
            count
        ) % {
            'count': count,
        }

    def object_action(self, instance, form=None):
        pass

    def view_action(self, form=None):
        self.action_count = 0

        for instance in self.get_queryset():
            try:
                self.object_action(form=form, instance=instance)
            except PermissionDenied:
                pass
            else:
                self.action_count += 1

        messages.success(
            self.request,
            self.get_success_message(count=self.action_count)
        )
