# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.template import Context
from django.template import Template
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class RenderedLabel:
    def __init__(self, content, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.content = content


class Category(models.Model):
    verbose_name = models.CharField(_('Category name'), db_index=True, max_length=250)
    verbose_name_plural = models.CharField(_('Pluralized category name'), db_index=True, max_length=250)

    def __str__(self):
        return self.verbose_name_plural or self.verbose_name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Object categories')


class State(models.Model):
    name = models.CharField(_('Name'), db_index=True, max_length=250)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('State')
        verbose_name_plural = _('Object states')


class PrintPaper(models.Model):
    name = models.CharField(_('Name'), db_index=True, max_length=250)
    paper_height = models.FloatField(_('Paper height'), blank=True, help_text=_('(mm)'), default=297)
    paper_width = models.FloatField(_('Paper width'), blank=True, help_text=_('(mm)'), default=210)
    margin_top = models.FloatField(_('Paper margin top'), blank=True, help_text=_('(mm)'))
    margin_left = models.FloatField(_('Paper margin left'), blank=True, help_text=_('(mm)'))
    label_height = models.FloatField(_('Label height'), blank=True, help_text=_('(mm)'), default=33.9)
    label_width = models.FloatField(_('Label width'), blank=True, help_text=_('(mm)'), default=63.5)
    column_space = models.FloatField(_('Space between label columns'), blank=True, help_text=_('(mm)'), default=5)
    row_space = models.FloatField(_('Space between label rows'), blank=True, help_text=_('(mm)'), default=5)
    column_number = models.IntegerField(_('Number of columns'), blank=True, help_text=_('(mm)'), default=1)
    row_number = models.IntegerField(_('Number of rows'), blank=True, help_text=_('(mm)'), default=1)
    background = models.FileField(_('Background'), blank=True, null=True, default=None, upload_to='backgrounds/')
    code_template = models.TextField(_('Label template'), blank=True, null=True, default=None,
                                     help_text=_('Django template used for each label, '
                                                 'with `paper` and `code` variables.'))
    css_template = models.TextField(_('CSS template'), blank=True, default='',
                                    help_text=_('Django template that must render a CSS sheet, '
                                                'used in the rendered page, with `paper` variable.'))

    class Meta:
        verbose_name = _('Print paper')
        verbose_name_plural = _('Print papers')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_pages_data = []
        self.current_page_data = []
        self.current_row_data = []

    def __str__(self):
        return self.name

    # noinspection PyTypeChecker
    def add_code(self, rendered_code):
        # noinspection PyTypeChecker
        y = len(self.all_pages_data) * self.paper_height \
            + len(self.current_page_data) * (self.label_height + self.row_space) \
            + self.margin_top
        x = len(self.current_row_data) * (self.label_width + self.column_space) + self.margin_left
        self.current_row_data.append(RenderedLabel(rendered_code, x=x, y=y))
        if len(self.current_row_data) == self.column_number:
            self.current_page_data.append(self.current_row_data)
            self.current_row_data = []
        if len(self.current_page_data) == self.row_number:
            self.all_pages_data.append(self.current_page_data)
            self.current_page_data = []

    def close(self):
        if self.current_row_data:
            # noinspection PyTypeChecker
            # self.current_row_data += [None] * (self.column_number - len(self.current_row_data))
            self.current_page_data.append(self.current_row_data)
            self.current_row_data = []
        if self.current_page_data:
            # noinspection PyTypeChecker
            # self.current_page_data += [[None] * self.column_number] * (self.row_number - len(self.current_page_data))
            self.all_pages_data.append(self.current_page_data)
            self.current_page_data = []

    def render(self):
        template_values = {'paper': self}
        if self.css_template:
            template = Template(self.css_template)
            return template.render(Context(template_values))
        return render_to_string('default_paper.css', template_values)


class Element(models.Model):
    category = models.ForeignKey(Category, db_index=True, blank=True, null=True, default=None)
    state = models.ForeignKey(State, db_index=True, blank=True, null=True, default=None)
    name = models.CharField(_('Name'), db_index=True, max_length=250)
    comment = models.TextField(_('Comment'), blank=True, default='')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Owner'),
                              db_index=True, blank=True, null=True, default=None)
    serial = models.CharField(_('Serial number'), db_index=True, max_length=250, blank=True, null=True, default=None)
    added_on = models.DateTimeField(_('Added on'), db_index=True, auto_now_add=True)
    modified_on = models.DateTimeField(_('Last modified'), db_index=True, auto_now=True)
    long_identifier = models.CharField(_('Long identifier'), db_index=True, null=True, blank=True, max_length=300)
    short_identifier = models.CharField(_('Short identifier'), db_index=True, null=True, blank=True, max_length=30)

    def save(self, *args, **kwargs):
        if not self.long_identifier:
            url = reverse('admin:%s_%s_change' % (self._meta.app_label, self._meta.model_name), args=[self.pk])
            self.long_identifier = '%s%s' % (settings.SERVER_BASE_URL[:-1], url)
        if not self.short_identifier and self.pk:
            self.short_identifier = '%012d' % (settings.BARCODE_PREFIX + self.pk)
        super().save(*args, **kwargs)
        if not self.short_identifier:
            self.short_identifier = '%012d' % (settings.BARCODE_PREFIX + self.pk)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Registered object')
        verbose_name_plural = _('Registered objects')


class Code(models.Model):
    identifier = models.CharField(_('Identifier'), db_index=True, max_length=250)
    name = models.CharField(_('Name'), db_index=True, max_length=250, blank=True, null=True)
    serial = models.CharField(_('Serial number'), db_index=True, max_length=250, blank=True, null=True, default=None)
    comment = models.TextField(_('Comment'), blank=True, default='')
    long_identifier = models.CharField(_('Long identifier'), db_index=True, max_length=300, blank=True, null=True)
    short_identifier = models.CharField(_('Short identifier'), db_index=True, max_length=30, blank=True, null=True)
    rfid_code = models.CharField(_('RFID identifier'), db_index=True, max_length=250, blank=True, null=True)

    class Meta:
        verbose_name = _('Code')
        verbose_name_plural = _('Codes')

    def __str__(self):
        return self.name

    def render(self, paper):
        template_values = {'code': self, 'paper': paper}
        if paper.css_template:
            template = Template(paper.css_template)
            return template.render(Context(template_values))
        return render_to_string('default_code.html', template_values)
