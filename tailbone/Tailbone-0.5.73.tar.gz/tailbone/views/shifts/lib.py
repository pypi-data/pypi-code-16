# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Base views for time sheets
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail import enum
from rattail.db import model, api
from rattail.time import localtime, make_utc, get_sunday

import formencode as fe
from pyramid_simpleform import Form
from webhelpers.html import HTML

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View


class ShiftFilter(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    store = forms.validators.ValidStore()
    department = forms.validators.ValidDepartment()
    date = fe.validators.DateConverter()


class EmployeeShiftFilter(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    employee = forms.validators.ValidEmployee()
    date = fe.validators.DateConverter()


class TimeSheetView(View):
    """
    Base view for time sheets.
    """
    key = None
    title = None
    model_class = None

    # Set this to False to avoid the default behavior of auto-filtering by
    # current store.
    default_filter_store = True

    @classmethod
    def get_title(cls):
        return cls.title or cls.key.capitalize()

    def get_timesheet_context(self):
        """
        Determine date/store/dept context from user's session and/or defaults.
        """
        date = None
        date_key = 'timesheet.{}.date'.format(self.key)
        if date_key in self.request.session:
            date_value = self.request.session.get(date_key)
            if date_value:
                try:
                    date = datetime.datetime.strptime(date_value, '%m/%d/%Y').date()
                except ValueError:
                    pass
        if not date:
            date = localtime(self.rattail_config).date()

        store = None
        department = None
        store_key = 'timesheet.{}.store'.format(self.key)
        department_key = 'timesheet.{}.department'.format(self.key)
        if store_key in self.request.session or department_key in self.request.session:
            store_uuid = self.request.session.get(store_key)
            if store_uuid:
                store = Session.query(model.Store).get(store_uuid) if store_uuid else None
            department_uuid = self.request.session.get(department_key)
            if department_uuid:
                department = Session.query(model.Department).get(department_uuid)
        else: # no store/department in session
            if self.default_filter_store:
                store = self.rattail_config.get('rattail', 'store')
                if store:
                    store = api.get_store(Session(), store)

        employees = Session.query(model.Employee)\
                           .filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)
        if store:
            employees = employees.join(model.EmployeeStore)\
                                 .filter(model.EmployeeStore.store == store)
        if department:
            employees = employees.join(model.EmployeeDepartment)\
                                 .filter(model.EmployeeDepartment.department == department)

        return {
            'date': date,
            'store': store,
            'department': department,
            'employees': employees.all(),
        }

    def get_employee_context(self):
        """
        Determine employee/date context from user's session and/or defaults
        """
        date = None
        date_key = 'timesheet.{}.employee.date'.format(self.key)
        if date_key in self.request.session:
            date_value = self.request.session.get(date_key)
            if date_value:
                try:
                    date = datetime.datetime.strptime(date_value, '%m/%d/%Y').date()
                except ValueError:
                    pass
        if not date:
            date = localtime(self.rattail_config).date()

        employee = None
        employee_key = 'timesheet.{}.employee'.format(self.key)
        if employee_key in self.request.session:
            employee_uuid = self.request.session[employee_key]
            employee = Session.query(model.Employee).get(employee_uuid) if employee_uuid else None
        if not employee:
            employee = self.request.user.employee

        # force current user if not allowed to view all data
        if not self.request.has_perm('{}.viewall'.format(self.key)):
            employee = self.request.user.employee
            assert employee

        return {'date': date, 'employee': employee}

    def process_filter_form(self, form):
        """
        Process a "shift filter" form if one was in fact POST'ed.  If it was
        then we store new context in session and redirect to display as normal.
        """
        if self.request.method == 'POST':
            if form.validate():
                store = form.data['store']
                self.request.session['timesheet.{}.store'.format(self.key)] = store.uuid if store else None
                department = form.data['department']
                self.request.session['timesheet.{}.department'.format(self.key)] = department.uuid if department else None
                date = form.data['date']
                self.request.session['timesheet.{}.date'.format(self.key)] = date.strftime('%m/%d/%Y') if date else None
                raise self.redirect(self.request.current_route_url())

    def process_employee_filter_form(self, form):
        """
        Process an "employee shift filter" form if one was in fact POST'ed.  If it
        was then we store new context in session and redirect to display as normal.
        """
        if self.request.method == 'POST':
            if form.validate():
                employee = form.data['employee']
                self.request.session['timesheet.{}.employee'.format(self.key)] = employee.uuid if employee else None
                date = form.data['date']
                self.request.session['timesheet.{}.employee.date'.format(self.key)] = date.strftime('%m/%d/%Y') if date else None
                raise self.redirect(self.request.current_route_url())

    def full(self):
        """
        View a "full" timesheet/schedule, i.e. all employees but filterable by
        store and/or department.
        """
        form = Form(self.request, schema=ShiftFilter)
        self.process_filter_form(form)
        context = self.get_timesheet_context()
        context['form'] = form
        return self.render_full(**context)

    def employee(self):
        """
        View time sheet for single employee.
        """
        form = Form(self.request, schema=EmployeeShiftFilter)
        self.process_employee_filter_form(form)
        context = self.get_employee_context()
        context['form'] = form
        return self.render_single(**context)

    def crossview(self):
        """
        Update session storage to so 'other' view reflects current view
        filters, then redirect to other view.
        """
        other_key = 'timesheet' if self.key == 'schedule' else 'schedule'

        # TODO: this check is pretty hacky..
        # employee time sheet
        if 'employee' in self.request.get_referrer():
            self.session_put('employee', self.session_get('employee'), mainkey=other_key)
            self.session_put('employee.date', self.session_get('employee.date'), mainkey=other_key)
            return self.redirect(self.request.route_url('{}.employee'.format(other_key)))

        else: # full time sheet
            self.session_put('store', self.session_get('store'), mainkey=other_key)
            self.session_put('department', self.session_get('department'), mainkey=other_key)
            self.session_put('date', self.session_get('date'), mainkey=other_key)
            return self.redirect(self.request.route_url(other_key))

    def session_get(self, key, mainkey=None):
        if mainkey is None:
            mainkey = self.key
        return self.request.session.get('timesheet.{}.{}'.format(mainkey, key))

    def session_put(self, key, value, mainkey=None):
        if mainkey is None:
            mainkey = self.key
        self.request.session['timesheet.{}.{}'.format(mainkey, key)] = value

    def get_stores(self):
        return Session.query(model.Store).order_by(model.Store.id).all()

    def get_store_options(self, stores):
        options = [(s.uuid, "{} - {}".format(s.id, s.name)) for s in stores]
        options.insert(0, ('', "(all)"))
        return options

    def get_departments(self):
        return Session.query(model.Department).order_by(model.Department.name).all()

    def get_department_options(self, departments):
        options = [(d.uuid, d.name) for d in departments]
        options.insert(0, ('', "(all)"))
        return options

    def render_full(self, date=None, employees=None, store=None, department=None, form=None, **kwargs):
        """
        Render a time sheet for one or more employees, for the week which
        includes the specified date.
        """
        sunday = get_sunday(date)
        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, %Y'), saturday.strftime('%a %b %d, %Y'))

        self.modify_employees(employees, weekdays)

        stores = self.get_stores()
        store_options = self.get_store_options(stores)

        departments = self.get_departments()
        department_options = self.get_department_options(departments)

        context = {
            'page_title': "Full {}".format(self.get_title()),
            'form': forms.FormRenderer(form) if form else None,
            'employees': employees,
            'stores': stores,
            'store_options': store_options,
            'store': store,
            'departments': departments,
            'department_options': department_options,
            'department': department,
            'week_of': week_of,
            'sunday': sunday,
            'prev_sunday': sunday - datetime.timedelta(days=7),
            'next_sunday': sunday + datetime.timedelta(days=7),
            'weekdays': weekdays,
            'permission_prefix': self.key,
            'render_shift': self.render_shift,
        }
        context.update(kwargs)
        return context

    def render_shift(self, shift):
        return HTML.tag('span', c=shift.get_display(self.rattail_config))

    def render_single(self, date=None, employee=None, form=None, **kwargs):
        """
        Render a time sheet for one employee, for the week which includes the
        specified date.
        """
        sunday = get_sunday(date)
        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, %Y'), saturday.strftime('%a %b %d, %Y'))

        self.modify_employees([employee], weekdays)

        context = {
            'page_title': "Employee {}".format(self.get_title()),
            'form': forms.FormRenderer(form) if form else None,
            'employee': employee,
            'employees': [employee],
            'week_of': week_of,
            'sunday': sunday,
            'prev_sunday': sunday - datetime.timedelta(days=7),
            'next_sunday': sunday + datetime.timedelta(days=7),
            'weekdays': weekdays,
            'permission_prefix': self.key,
            'render_shift': self.render_shift,
        }
        context.update(kwargs)
        return context

    def modify_employees(self, employees, weekdays):
        min_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[0], datetime.time(0)))
        max_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[-1] + datetime.timedelta(days=1), datetime.time(0)))
        shifts = Session.query(self.model_class)\
                        .filter(self.model_class.employee_uuid.in_([e.uuid for e in employees]))\
                        .filter(self.model_class.start_time >= make_utc(min_time))\
                        .filter(self.model_class.start_time < make_utc(max_time))\
                        .all()

        for employee in employees:
            employee_shifts = sorted([s for s in shifts if s.employee_uuid == employee.uuid],
                                     key=lambda s: (s.start_time, s.end_time))
            employee.weekdays = []
            employee.hours = datetime.timedelta(0)
            employee.hours_display = '0'

            for day in weekdays:
                empday = {
                    'shifts': [],
                    'hours': datetime.timedelta(0),
                    'hours_display': '',
                }

                while employee_shifts:
                    shift = employee_shifts[0]
                    if shift.employee_uuid != employee.uuid:
                        break
                    elif shift.get_date(self.rattail_config) == day:
                        empday['shifts'].append(shift)
                        length = shift.length
                        if length is not None:
                            empday['hours'] += shift.length
                            employee.hours += shift.length
                        del employee_shifts[0]
                    else:
                        break

                if empday['hours']:
                    minutes = (empday['hours'].days * 1440) + (empday['hours'].seconds / 60)
                    empday['hours_display'] = '{}:{:02d}'.format(minutes // 60, minutes % 60)
                employee.weekdays.append(empday)

            if employee.hours:
                minutes = (employee.hours.days * 1440) + (employee.hours.seconds / 60)
                employee.hours_display = '{}:{:02d}'.format(minutes // 60, minutes % 60)

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a time sheet view.
        """
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):
        """
        Provide default configuration for a time sheet view.
        """
        title = cls.get_title()
        config.add_tailbone_permission_group(cls.key, title)
        config.add_tailbone_permission(cls.key, '{}.view'.format(cls.key), "View single employee {}".format(title))
        config.add_tailbone_permission(cls.key, '{}.viewall'.format(cls.key), "View full {}".format(title))

        # full time sheet
        config.add_route(cls.key, '/{}/'.format(cls.key))
        config.add_view(cls, attr='full', route_name=cls.key,
                        renderer='/shifts/{}.mako'.format(cls.key),
                        permission='{}.viewall'.format(cls.key))

        # single employee time sheet
        config.add_route('{}.employee'.format(cls.key), '/{}/employee/'.format(cls.key))
        config.add_view(cls, attr='employee', route_name='{}.employee'.format(cls.key),
                        renderer='/shifts/{}.mako'.format(cls.key),
                        permission='{}.view'.format(cls.key))

        # goto cross-view (view 'timesheet' as 'schedule' or vice-versa)
        other_key = 'timesheet' if cls.key == 'schedule' else 'schedule'
        config.add_route('{}.goto.{}'.format(cls.key, other_key), '/{}/goto-{}'.format(cls.key, other_key))
        config.add_view(cls, attr='crossview', route_name='{}.goto.{}'.format(cls.key, other_key),
                        permission='{}.view'.format(other_key))
