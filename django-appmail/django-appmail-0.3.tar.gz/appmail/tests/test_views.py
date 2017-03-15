# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from .. import views
from ..models import EmailTemplate


class ViewTests(TestCase):

    """appmail.helpers module tests."""

    def test_render_template_subject(self):
        template = EmailTemplate(subject='foo').save()
        print template

    def test_render_template_body(self):
        pass
