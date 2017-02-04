# -*- coding: utf-8 -*-
from django.template import loader
from django.template.response import TemplateResponse


def no_access(request):
    """No access view"""
    template = loader.get_template('yaacl/no_access.html')

    return TemplateResponse(request, template)
