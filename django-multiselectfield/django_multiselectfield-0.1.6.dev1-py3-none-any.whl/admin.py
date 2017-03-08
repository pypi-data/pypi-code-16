from django.contrib.admin.filters import ChoicesFieldListFilter
from django.utils.translation import ugettext_lazy as _


class MSFChoicesFieldListFilter(ChoicesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__contains' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        super(ChoicesFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)


def msf_filter(field_name, parameter_name=None):
    """
    Helper function to allow users to simply specify a list of fields in
    `list_filter`
    """
    class MSFFieldChoicesFieldListFilter(MSFChoicesFieldListFilter):
        title = _(field_name)
        parameter_name = field_name if parameter_name is None else parameter_name

    return MSFFieldChoicesFieldListFilter
