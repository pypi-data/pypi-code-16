# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from ..models import Category, Document


register = template.Library()


@register.assignment_tag
def get_latest_documents(count=5, category=None):
    """ Accepts category or category slug. """

    document_list = Document.objects.published()

    # Optional filter by category
    if category is not None:
        if isinstance(category, Category):
            document_list = document_list.filter(category=category)
        else:
            document_list = document_list.filter(category__slug=category)

    return document_list[:count]
