from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode

def _get_node(template, context=Context(), name='subject'):
    for i, node in enumerate(template):
        if isinstance(node, BlockNode) and node.name == name:
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            return _get_node(node.nodelist, context, name)
    raise Exception("Node '%s' could not be found in template." % name)