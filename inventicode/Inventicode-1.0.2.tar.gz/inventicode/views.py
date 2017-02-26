# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.admin import site
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache

from inventicode.forms import PrintForm, UpdateCategoryForm, UpdateStateForm, BatchUpdateForm
from inventicode.models import Code, PrintPaper, Element

__author__ = 'Matthieu Gallet'


# views:
#   print page (object selection, paper selection, case selection)
#   import a CSV of objects
#   import a CSV of existing codes
#   add an existing code to a object
#   identify a code


@login_required
@never_cache
def print_labels(request, queryset=None):
    if queryset:
        form = PrintForm(initial={'elements': queryset})
    elif request.method == 'POST':
        form = PrintForm(request.POST)
        if form.is_valid():
            elements = form.cleaned_data['elements']
            required_identifiers = {str(x.id): x for x in elements}
            # required_identifiers[element.id] = True if a Code is defined
            existing_codes = {x.identifier: x for x in Code.objects.filter(identifier__in=required_identifiers)}
            new_codes = [Code(identifier=str(x.id),
                              comment=x.comment, serial=x.serial,
                              long_identifier=x.long_identifier,
                              short_identifier=x.short_identifier, name=x.name)
                         for x in required_identifiers.values() if str(x.id) not in existing_codes]
            Code.objects.bulk_create(new_codes)
            for code in existing_codes.values():
                element = required_identifiers[code.identifier]
                for attr_name in ('name', 'comment', 'serial', 'long_identifier', 'short_identifier'):
                    setattr(code, attr_name, getattr(element, attr_name))
            all_codes = new_codes + list(existing_codes.values())
            paper = form.cleaned_data['paper']
            excluded_cases_str = form.cleaned_data['excluded_cases']
            return codes_to_html(request, all_codes, paper, excluded_cases_str)
    else:
        form = PrintForm()
    template_values = {'form': form, 'site_header': site.site_header, 'action_url': reverse('print_labels')}
    return TemplateResponse(request, 'print_form.html', template_values)


@login_required
@never_cache
def batch_update(request):
    if request.method == 'POST':
        form = BatchUpdateForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            new_state = form.cleaned_data['state']
            new_category = form.cleaned_data['category']
            kwargs = {}
            if form.cleaned_data['apply_state']:
                kwargs['state'] = new_state
            if form.cleaned_data['apply_category']:
                kwargs['category'] = new_category
            if not form.cleaned_data['apply_state'] and not form.cleaned_data['apply_category']:
                messages.warning(request, _('You should modify the state or the category.'))
            else:
                query = Element.objects.filter(Q(long_identifier=identifier) | Q(short_identifier=identifier))
                n = query.update(**kwargs)
                if n == 0:
                    msg = _('No object corresponding to %(i)s has been found.') % {'i': identifier}
                elif n == 1:
                    if form.cleaned_data['apply_state'] and form.cleaned_data['apply_category']:
                        msg = _('State of object %(o)s set to %(s)s and category set to %(c)s.') % \
                              {'o': query.first(), 's': new_state, 'c': new_category}
                    elif form.cleaned_data['apply_state']:
                        msg = _('State of object %(o)s set to %(s)s.') % {'o': query.first(), 's': new_state}
                    else:
                        msg = _('Category of object %(o)s set to %(c)s.') % {'o': query.first(), 'c': new_category}
                else:
                    if form.cleaned_data['apply_state'] and form.cleaned_data['apply_category']:
                        msg = _('State of %(n)s objects set to %(s)s and category set to %(c)s.') % \
                              {'n': n, 's': new_state or _('empty'), 'c': new_category or _('empty')}
                    elif form.cleaned_data['apply_state']:
                        msg = _('State of %(n)s objects  set to %(s)s.') % {'n': n, 's': new_state or _('empty')}
                    else:
                        msg = _('Category of %(n)s objects set to %(c)s.') % {'n': n, 'c': new_category or _('empty')}
                messages.success(request, msg)
    else:
        form = BatchUpdateForm()
    template_values = {'form': form, 'site_header': site.site_header, 'action_url': reverse('batch_update')}
    return TemplateResponse(request, 'print_form.html', template_values)


@permission_required('inventicode.change_element')
def update_category(request, queryset=None):
    if queryset:
        form = UpdateCategoryForm(initial={'elements': queryset})
    elif request.method == 'POST':
        form = UpdateCategoryForm(request.POST)
        if form.is_valid():
            elements = form.cleaned_data['elements']
            category = form.cleaned_data['category']
            c = Element.objects.filter(pk__in=elements).update(category=category)
            if c == 0:
                messages.success(request, _('No registered object has been updated.'))
            elif c == 1:
                messages.success(request, _('A registered object has been updated.'))
            else:
                messages.success(request, _('%(c)s registered objects have been updated.') % {'c': c})
            return redirect('admin:inventicode_element_changelist')
    else:
        form = UpdateCategoryForm()
    template_values = {'form': form, 'site_header': site.site_header, 'action_url': reverse('update_category')}
    return TemplateResponse(request, 'print_form.html', template_values)


@permission_required('inventicode.change_element')
def update_state(request, queryset=None):
    if queryset:
        form = UpdateStateForm(initial={'elements': queryset})
    elif request.method == 'POST':
        form = UpdateStateForm(request.POST)
        if form.is_valid():
            elements = form.cleaned_data['elements']
            state = form.cleaned_data['state']
            c = Element.objects.filter(pk__in=elements).update(state=state)
            if c == 0:
                messages.success(request, _('No registered object has been updated.'))
            elif c == 1:
                messages.success(request, _('A registered object has been updated.'))
            else:
                messages.success(request, _('%(c)s registered objects have been updated.') % {'c': c})
            return redirect('admin:inventicode_element_changelist')
    else:
        form = UpdateStateForm()
    template_values = {'form': form, 'site_header': site.site_header, 'action_url': reverse('update_state')}
    return TemplateResponse(request, 'print_form.html', template_values)


def codes_to_html(request, printed_codes, paper, excluded_cases_str):
    assert isinstance(paper, PrintPaper)
    excluded_cases = set()
    if excluded_cases_str:
        for value in excluded_cases_str.split(','):
            start, sep, end = value.partition('-')
            if sep == '-':
                excluded_cases |= set(range(int(start), int(end) + 1))
            else:
                excluded_cases.add(int(start))
    label_index = 0
    for code in printed_codes:
        while label_index + 1 in excluded_cases:
            paper.add_code(None)
            label_index += 1
        paper.add_code(code.render(paper))
        label_index += 1
    paper.close()
    return TemplateResponse(request, 'print_page.html', {'paper': paper})


def index(request):
    return HttpResponseRedirect(reverse('admin:index'))
