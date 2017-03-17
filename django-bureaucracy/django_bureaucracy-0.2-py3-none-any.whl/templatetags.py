import warnings

from django import template
from django.template import TemplateSyntaxError

from bureaucracy.powerpoint.placeholders import (
    CONTEXT_KEY_FOR_PLACEHOLDER, AlreadyRenderedException
)
from bureaucracy.powerpoint.slides import CONTEXT_KEY_FOR_SLIDE

register = template.Library()


class PPTTagNode(template.Node):
    def render_in_place(self, context, placeholder):
        raise NotImplementedError

    def render(self, context):
        try:
            placeholder = context[CONTEXT_KEY_FOR_PLACEHOLDER]
            self.render_in_place(context, placeholder)
        except KeyError:
            warnings.warn("placeholder was not found in context passed to template tag {}. it will not be "
                          "rendered.".format(self.__class__))
        raise AlreadyRenderedException


class LinkNode(PPTTagNode):
    def __init__(self, url_expr, title_expr):
        self.url_expr = url_expr
        self.title_expr = title_expr

    def render_in_place(self, context, placeholder):
        url, title = self.url_expr.resolve(context), self.title_expr.resolve(context)
        placeholder.insert_link(url, title)


@register.tag
def link(parser, token):
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError("The '%r' tag requires two arguments: url and title", bits[0])
    url_expr, title_expr = parser.compile_filter(bits[1]), parser.compile_filter(bits[2])
    return LinkNode(url_expr, title_expr)


class RepeatUntilEmptyNode(PPTTagNode):
    def __init__(self, objects_expr):
        self.objects_expr = objects_expr

    def render_in_place(self, context, placeholder):
        objects = self.objects_expr.resolve(context)

        placeholder.remove()

        if objects:
            context[CONTEXT_KEY_FOR_SLIDE].insert_another()


@register.tag
def repeatwhile(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("The '%r' tag requires one argument: an iterable to check.")
    objects_expr = parser.compile_filter(bits[1])
    return RepeatUntilEmptyNode(objects_expr)


class PopNode(PPTTagNode):
    def __init__(self, objects_expr, var_expr):
        self.objects_expr = objects_expr
        self.var_expr = var_expr

    def render_in_place(self, context, placeholder):
        placeholder.remove()
        objects = self.objects_expr.resolve(context)
        if len(objects) > 0:
            context[self.var_expr.var.var] = objects.pop(0)
        else:
            del context[self.var_expr.var.var]


@register.tag
def pop(parser, token):
    bits = token.split_contents()
    if len(bits) != 4:
        raise TemplateSyntaxError(
            "The %(tag)r tag requires an iterable and as-var: "
            "{% %(tag)r my_list as my_item %}", tag=bits[0]
        )

    if bits[2] != 'as':
        raise TemplateSyntaxError("The %r tag must assign with the 'as' token")

    objects_expr = parser.compile_filter(bits[1])
    var_expr = parser.compile_filter(bits[3])
    return PopNode(objects_expr, var_expr)
