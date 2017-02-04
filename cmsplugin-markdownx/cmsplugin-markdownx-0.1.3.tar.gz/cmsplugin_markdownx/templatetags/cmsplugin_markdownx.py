from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe, SafeString
from django.conf import settings
from django.utils.module_loading import import_string


from markdownx import settings as md_settings       # access MARKDOWNX_xxx settings with canonical default values

register = template.Library()

@register.filter(needs_autoescape=True)
def markdownify(text:str, autoescape:bool=True) ->SafeString:
    """convert text to html, using the preconfigured markdown settings
    :param text: markdown string to render
    :param autoescape: True if template operating in autoescape mode.
                        But ignored, because markdown allows embedded html.
    :returns: stream of HTML. First tag will be stylesheet. Not enclosed in a block.
              If you need that, do it in  the template.
    """

    retVal = ''     ## failsafe return value
    mdf = import_string(md_settings.MARKDOWNX_MARKDOWNIFY_FUNCTION)
    if mdf is not None:
        retVal = mdf( text)
        #css = getattr( settings, "CMSPLUGIN_MARKDOWNX_CODEHILITE_CSS")
        #if css:
        #    retVal = r'''<link rel="stylesheet" type="text/css" href="{}" />'''.format( css) + retVal
    return mark_safe(retVal)

@register.simple_tag
def get_setting(variable:str, default_value=None):
    """fetches the specified variable from Django settings (project settings.py first, then built-ins
    :param variable:   Name of setting
    :param default_value:    Default value if not found or not set
    :returns:          Corresponding value.  If it's `str`, it will be run through conditional escaping by the framework.
    """

    return getattr( settings, variable, default_value)

