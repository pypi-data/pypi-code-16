# -*- coding: utf-8 -*-
import re

from django.apps import apps
from django.contrib.admin import site, ModelAdmin
from django.utils.translation import ugettext_lazy as _

from inventicode.models import Category, Element, State, PrintPaper
from inventicode.views import print_labels, update_category, update_state


class DuplicateAdmin(ModelAdmin):
    duplicate_model = None
    duplicate_name_field = 'name'
    duplicate_excluded_fields = {'id'}
    actions = ['duplicate']

    def duplicate(self, request, queryset):
        existing_names = {x[0] for x in self.duplicate_model.objects.all().values_list(self.duplicate_name_field)}
        # noinspection PyProtectedMember
        fields = [x.name for x in self.duplicate_model._meta.get_fields()
                  if x.name not in self.duplicate_excluded_fields]

        def duplicate_obj(obj_):
            kwargs = {x: getattr(obj_, x) for x in fields}
            index, name = 2, obj_.name
            matcher = re.match('^(.*) \((\d+)\)$', obj_.name)
            if matcher:
                index = int(matcher.group(2)) + 1
                name = matcher.group(1)
            while '%s (%s)' % (name, index) in existing_names:
                index += 1
            kwargs[self.duplicate_name_field] = '%s (%s)' % (name, index)
            existing_names.add(kwargs[self.duplicate_name_field])
            return self.duplicate_model(**kwargs)
        count = 0
        for obj in queryset:
            new_obj = duplicate_obj(obj)
            new_obj.save()
            count += 1
        if count == 1:
            msg = _('1 object has been duplicated.')
        else:
            msg = _('%(c)d objects have been duplicated.') % {'c': count}
        self.message_user(request, msg)

    duplicate.short_description = _('Duplicate selection')


class ElementAdmin(DuplicateAdmin):
    change_list_template = None
    duplicate_model = Element
    duplicate_excluded_fields = {'id', 'long_identifier', 'short_identifier'}
    search_fields = ('name', 'serial', 'short_identifier', 'long_identifier')
    list_display = ('name', 'serial', 'category', 'state', 'owner', 'modified_on')
    list_filter = ('category', 'state', 'owner', 'modified_on')
    list_editable = ('serial', 'category', 'state', 'owner')
    exclude = ('short_identifier', 'long_identifier')
    fields = ('name', 'serial', ('category', 'state', 'owner'), 'comment', ('added_on', 'modified_on'))
    readonly_fields = ('added_on', 'modified_on')

    def print_elements_action(self, request, queryset):
        return print_labels(request, queryset)
    print_elements_action.short_description = _('Print labels for selected objects')

    def update_category_action(self, request, queryset):
        return update_category(request, queryset)
    update_category_action.short_description = _('Update the object category')

    def update_state_action(self, request, queryset):
        return update_state(request, queryset)
    update_state_action.short_description = _('Update the object state')
    actions = ['duplicate', 'print_elements_action', 'update_category_action', 'update_state_action']


class PrintPaperAdmin(DuplicateAdmin):
    duplicate_model = PrintPaper
    search_fields = ('name', )
    list_display = ('name', 'paper_height', 'paper_width', 'margin_top', 'margin_left',
                    'column_space', 'row_space', 'column_number', 'row_number')
    list_editable = ('paper_height', 'paper_width', 'margin_top', 'margin_left', 'column_space', 'row_space',
                     'column_number', 'row_number')
    fields = ('name', ('paper_width', 'paper_height', 'background'),
              ('column_number', 'row_number'), ('label_width', 'label_height'),
              ('margin_top', 'margin_left'), ('column_space', 'row_space'),
              'code_template', 'css_template')
#
#
# class CodeAdmin(ModelAdmin):
#     search_fields = ('name', 'long_identifier', 'short_identifier', 'rfid_code')
#     list_display = ('name', 'long_identifier', 'short_identifier', 'rfid_code')
site.site_header = 'InventiCode'
site.register(Category)
site.register(State)
site.register(PrintPaper, PrintPaperAdmin)
site.register(Element, ElementAdmin)
# site.register(Code, CodeAdmin)

app = apps.get_app_config('inventicode')
app.verbose_name = _('Models of paper and registered objects')
