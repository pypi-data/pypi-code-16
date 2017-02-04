from .mixins import TemplateMixin


class View(object):
    def __call__(self, request, *args, **kwargs):
        return self.dispatch(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        method_name = request.method.lower()
        method = getattr(self, method_name, self._not_implemented)

        return method(request, *args, **kwargs)

    def _not_implemented(self, request):
        method_name = request.method.lower()
        raise NotImplementedError(
            '\'%s.%s\' method is not implemented.' % (
                self.__class__.__name__,
                method_name,
            ),
        )


class TemplateView(TemplateMixin, View):
    """In this case, method must return dict, that is used to populate data
    in template"""
    pass
