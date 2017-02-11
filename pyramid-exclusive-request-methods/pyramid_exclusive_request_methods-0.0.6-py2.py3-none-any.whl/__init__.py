from zope.interface import implementedBy, Interface
from zope.interface.interfaces import IInterface
from pyramid.config.predicates import RequestMethodPredicate
from pyramid.config.util import MAX_ORDER
try:
    from pyramid.util import as_sorted_tuple
except ImportError:
    from pyramid.config.util import as_sorted_tuple
from pyramid.compat import string_types, text_type
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.viewderivers import predicated_view, INGRESS
from pyramid.interfaces import IRequest, IRouteRequest, IView, IViewClassifier, ISecuredView, IMultiView
from pyramid.view import view_config
from pyramid.util import viewdefaults


class Info(object):
    def __init__(self, route_name=None, context=None, name="", **_):
        self.route_name = route_name
        self.context = context
        self.name = name


class ExclusiveView(object):
    def __init__(self, wrapped, request_methods):
        self.wrapped = wrapped
        self.request_methods = request_methods

    def __call__(self, context, request):
        if request.method not in self.request_methods:
            raise HTTPMethodNotAllowed(text=u'Predicate mismatch for view %s (request_method = %s)' % (getattr(self.wrapped, '__name__', self.wrapped), ','.join(self.request_methods)))
        return self.wrapped(context, request)


def find_existing_views(registry, route_name, context, name):
    if route_name:
        request_iface = registry.queryUtility(IRouteRequest, name=route_name)
    else:
        request_iface = IRequest
    if context is None:
        context = Interface
    if not IInterface.providedBy(context):
        context = implementedBy(context)

    for view_type in (IView, ISecuredView, IMultiView):
        view = registry.adapters.registered(
            (IViewClassifier, request_iface, context),
            view_type,
            name
            )
        if view is not None:
            if view_type is IMultiView:
                return [_view for _, _view, _ in view.views]
            else:
                return [view]
    return []


def find_existing_exclusive_view(registry, route_name, context, name):
    views = find_existing_views(registry, route_name, context, name) 
    for view in views:
        while view is not None:
            if isinstance(view, ExclusiveView):
                return view
            view = getattr(view, '__wraps__', None)
    return None


def exclusive_request_method_view_deriver(view, info):
    request_method_pred = None
    for pred in info.predicates:
        if isinstance(pred, RequestMethodPredicate):
            request_method_pred = pred
            break
    if request_method_pred is not None:
        extra_info = getattr(info.original_view, '__pyramid_exclusive_request_methods__', None)
        if extra_info is not None:
            old_view = find_existing_exclusive_view(info.registry, extra_info.route_name, extra_info.context, extra_info.name)
            if old_view is None:
                request_methods = request_method_pred.val
                info.predicates.remove(request_method_pred)
                info.order = MAX_ORDER + 1 # make sure that the view has the lowest precedence.
                return ExclusiveView(view, request_methods)
    return view


Unspecified = object()


def add_exclusive_view(
        config,
        view=Unspecified,
        name=Unspecified,
        for_=Unspecified,
        permission=Unspecified,
        request_type=Unspecified,
        route_name=Unspecified,
        request_method=Unspecified,
        request_param=Unspecified,
        containment=Unspecified,
        attr=Unspecified,
        renderer=Unspecified,
        wrapper=Unspecified,
        xhr=Unspecified,
        accept=Unspecified,
        header=Unspecified,
        path_info=Unspecified,
        custom_predicates=Unspecified,
        context=Unspecified,
        decorator=Unspecified,
        mapper=Unspecified,
        http_cache=Unspecified,
        match_param=Unspecified,
        check_csrf=Unspecified,
        require_csrf=Unspecified,
        **view_options):
    if view is not Unspecified:
        view_options['view'] = view
    if name is not Unspecified:
        view_options['name'] = name
    if for_ is not Unspecified:
        view_options['for_'] = for_
    if permission is not Unspecified:
        view_options['permission'] = permission
    if request_type is not Unspecified:
        view_options['request_type'] = request_type
    if route_name is not Unspecified:
        view_options['route_name'] = route_name
    if request_method is not Unspecified:
        view_options['request_method'] = request_method
    if request_param is not Unspecified:
        view_options['request_param'] = request_param
    if containment is not Unspecified:
        view_options['containment'] = containment
    if attr is not Unspecified:
        view_options['attr'] = attr
    if renderer is not Unspecified:
        view_options['renderer'] = renderer
    if wrapper is not Unspecified:
        view_options['wrapper'] = wrapper
    if xhr is not Unspecified:
        view_options['xhr'] = xhr
    if accept is not Unspecified:
        view_options['accept'] = accept
    if header is not Unspecified:
        view_options['header'] = header
    if path_info is not Unspecified:
        view_options['path_info'] = path_info
    if custom_predicates is not Unspecified:
        view_options['custom_predicates'] = custom_predicates
    if context is not Unspecified:
        view_options['context'] = context
    if decorator is not Unspecified:
        view_options['decorator'] = decorator
    if mapper is not Unspecified:
        view_options['mapper'] = mapper
    if http_cache is not Unspecified:
        view_options['http_cache'] = http_cache
    if match_param is not Unspecified:
        view_options['match_param'] = match_param
    if check_csrf is not Unspecified:
        view_options['check_csrf'] = check_csrf
    if require_csrf is not Unspecified:
        view_options['require_csrf'] = require_csrf
    extra_info = viewdefaults(lambda _, **kwargs: Info(**kwargs))(config, **view_options)
    setattr(view, '__pyramid_exclusive_request_methods__', extra_info)
    config.add_view(**view_options)


# stolen from pyramid.view
class exclusive_view_config(view_config):
    def __call__(self, wrapped):
        settings = self.__dict__.copy()
        depth = settings.pop('_depth', 0)

        def callback(context, name, ob):
            config = context.config.with_package(info.module)
            config.add_exclusive_view(view=ob, **settings)

        info = self.venusian.attach(wrapped, callback, category='pyramid',
                                    depth=depth + 1)

        if info.scope == 'class':
            if settings.get('attr') is None:
                settings['attr'] = wrapped.__name__

        settings['_info'] = info.codeinfo
        return wrapped


def includeme(config):
    config.add_view_deriver(exclusive_request_method_view_deriver, under=INGRESS)
    config.add_directive('add_exclusive_view', add_exclusive_view)
