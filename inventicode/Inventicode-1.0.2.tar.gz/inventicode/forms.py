# -*- coding: utf-8 -*-
import re

from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from inventicode.models import Element, PrintPaper, Category, State

__author__ = 'Matthieu Gallet'
matcher = re.compile(r'^|((\d+|\d+-\d+)(,\d+|,\d+-\d+)*)$')


class PrintForm(forms.Form):
    elements = forms.ModelMultipleChoiceField(Element.objects.all(), required=True,
                                              label=_('Registered objects'))
    paper = forms.ModelChoiceField(PrintPaper.objects.all(), label=_('Model of paper'))
    excluded_cases = forms.CharField(label=_('Excluded cases'),
                                     help_text=_('Separated by commas, 1: being the top left case, followed '
                                                 'by other cases from left to right and top to bottom.'),
                                     validators=[RegexValidator(matcher.pattern)],
                                     required=False)


class UpdateCategoryForm(forms.Form):
    elements = forms.ModelMultipleChoiceField(Element.objects.all(), required=True,
                                              label=_('Registered objects'))
    category = forms.ModelChoiceField(Category.objects.all(), required=False, label=_('New category'))


class UpdateStateForm(forms.Form):
    elements = forms.ModelMultipleChoiceField(Element.objects.all(), required=True,
                                              label=_('Registered objects'))
    state = forms.ModelChoiceField(State.objects.all(), required=False, label=_('New state'))


class BatchUpdateForm(forms.Form):
    identifier = forms.CharField(label=_('Short or long object identifier'))
    state = forms.ModelChoiceField(State.objects.all(), required=False, label=_('New state'))
    apply_state = forms.BooleanField(required=False, label=_('Modify the state'), initial=True)
    category = forms.ModelChoiceField(Category.objects.all(), required=False, label=_('New category'))
    apply_category = forms.BooleanField(required=False, label=_('Modify the category'), initial=False)
