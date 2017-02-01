from posixpath import join as urljoin
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()

DEFAULT_SETTINGS = {
    'source': 'dart/src',
    'build': 'dart/build',
}


def make_path(mapping, *path):
    staticmap = getattr(settings, 'STATICFILES_DART', DEFAULT_SETTINGS)
    root = staticmap.get(mapping, DEFAULT_SETTINGS[mapping])
    return static(urljoin(root, *path))


@register.simple_tag(takes_context=True)
def webcomponents(context, lite=False):
    if context.request.is_dartium: return ''
    path = make_path('build',
        'packages', 'web_components',
        'webcomponents-lite.min.js' if lite else 'webcomponents.min.js'
    )
    return mark_safe('<script src="{}"></script>'.format(path))


@register.simple_tag(takes_context=True)
def dart(context, file):
    if context.request.is_dartium:
        path = make_path('source', file)
        return mark_safe('<script type="application/dart" src="{}"></script>'.format(path))
    else:
        path = make_path('build', file+'.js')
        return mark_safe('<script src="{}"></script>'.format(path))

