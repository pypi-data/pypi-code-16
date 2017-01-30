"""
############################################
:mod:`pywebtools.testing` -- py.test plugins
############################################

The primary use point is the :func:`~pywebtools.testing.functional_tester`
fixture.

.. moduleauthor:: Mark Hall <mark.hall@work.room3b.eu>
"""
from __future__ import (absolute_import, division, print_function, unicode_literals)

import pytest

from pyramid.paster import get_app
from pyramid.request import Request
from webtest import TestApp


@pytest.yield_fixture
def app():
    """Fixture that provides a newly initialised pyramid application defined in "testing.ini"
    with an empty database.
    """
    # Create the application
    app = get_app('testing.ini')

    # Yield to the test
    yield app


class PyramidAppTester(object):
    """The :class:`~pywebtools.testing.RequestTester` provides functionality for testing requests
    in a Pyramid application
    """

    def __init__(self, app):
        self._app = app
        self._test = TestApp(app)
        self._response = None

    def goto(self, href, **kwargs):
        """Sends a request using the method specified in the ``method`` keyword argument. If a previous
        request has been made, then will use the :func:`~webtest.response.Response.goto` function to
        send the request, otherwise will use the :func:`~webtest.app.TestApp.get` or
        :func:`~webtest.app.TestApp.post` functions.
        """
        if 'headers' in kwargs:
            if isinstance(kwargs['headers'], dict):
                if 'Accept' not in headers:
                    kwargs['headers']['Accept'] = '*/*'
            elif isinstance(kwargs['headers'], list):
                if 'Accept' not in dict(kwargs['headers']):
                    kwargs['headers'].append(('Accept', '*/*'))
            else:
                assert False, 'Headers must be either a list or dict'
        else:
            kwargs['headers'] = [('Accept', '*/*')]
        if 'status' not in kwargs:
            kwargs['status'] = '*'
        if self._response:
            self._response = self._response.goto(href, **kwargs)
        else:
            if 'method' not in kwargs or kwargs['method'].lower() == 'get':
                valid_args = dict([(k, v) for k, v in kwargs.items() if k in ['params', 'headers', 'extra_environ',
                                                                              'status', 'expect_errors', 'xhr']])
                self._response = self._test.get(href, **valid_args)
            elif 'method' in kwargs and kwargs['method'].lower() == 'post':
                valid_args = dict([(k, v) for k, v in kwargs.items() if k in ['params', 'headers', 'extra_environ',
                                                                              'status', 'upload_files',
                                                                              'expect_errors', 'content_type', 'xhr']])
                self._response = self._test.post(href, **valid_args)
            else:
                assert kwargs['method'].lower() in ['get', 'post'], 'Only get and post requests are supported'
        
    def get(self, href, **kwargs):
        """Send a GET request to the given ``href``.

        :param href: The url to request
        :type href: ``unicode``
        """
        kwargs['method'] = 'get'
        self.goto(href, **kwargs)

    def post(self, href, **kwargs):
        """Send a POST request to the given ``href``.

        :param href: The url to request
        :type href: ``unicode``
        """
        kwargs['method'] = 'post'
        self.goto(href, **kwargs)

    def submit_form(self, form_id=None, form_idx=None, values=None, force_value=False, **kwargs):
        """Submits a form.

        :param form_id: The optional id value to use to select the form to submit 
        :type form_id: ``unicode``
        :param form_idx: The optional form index to select the form to submit
        :param form_idx: ``int``
        :param values: The values to set on the form before submitting
        :type values: ``dict``
        :param force_value: Force setting values on selects/checkboxes even if that value does not exist
        :type force_value: ``boolean`` 
        """
        if self._response:
            if form_id is not None:
                form = self._response.html.find_all(name='form', id=form_id)
                assert len(form) > 0, '0 forms found with the id %s' % form_id
                assert len(form) == 1, 'More than 1 form found with the id %s' % form_id
                form = form[0]
            elif form_idx is not None:
                form = self._response.html.find_all(name='form', id=form_id)
                assert len(form) > 0, '0 forms found'
                assert len(form) > form_idx + 1, 'No form at index %i' % form_idx
            else:
                form = self._response.html.find_all(name='form')
                assert len(form) > 0, '0 forms found'
                form = form[0]
            body = []
            has_files = False
            for field in form.find_all(name=lambda tag: tag.name in ['input', 'select', 'textarea'] and
                                   tag.has_attr('name')):
                name = field['name']
                if field.name == 'input':
                    field_type = field['type'] if field.has_attr('type') else 'text'
                    if field_type == 'checkbox':
                        if field.has_attr('value') and name in values:
                            if field['value'] in values[name]:
                                body.append((name, field['value']))
                            elif force_value:
                                if isinstance(values[name], list):
                                    for sub_value in values[name]:
                                        body.append((name, sub_value))
                                else:
                                    body.append((name, values[name]))
                        elif field.has_attr('value') and field.has_attr('checked'):
                            body.append((name, field['value']))
                        elif 'on' in values[name] or field.has_attr('checked'):
                            body.append((name, 'on'))
                        elif force_value and name in values:
                            if isinstance(values[name], list):
                                for sub_value in values[name]:
                                    body.append((name, sub_value))
                            else:
                                body.append((name, values[name]))
                    elif field_type == 'radio':
                        if field.has_attr('value') and name in values and field['value'] == values[name]:
                            body.append((name, str(values[name])))
                        elif field.has_attr('value') and field.has_attr('checked'):
                            body.append((name, field['value']))
                        elif 'on' == values[name] or field.has_attr('checked'):
                            body.append((name, 'on'))
                        elif force_value and name in values:
                            if isinstance(values[name], list):
                                for sub_value in values[name]:
                                    body.append((name, sub_value))
                            else:
                                body.append((name, values[name]))
                    elif field_type == 'file':
                        if name in values:
                            body.append((name, values[name]))
                    else:
                        if name in values:
                            body.append((name, str(values[name])))
                        elif field.has_attr('value'):
                            body.append((name, field['value']))
                        else:
                            body.append((name, ''))
                elif field.name == 'select':
                    if name in values:
                        option = field.find_all(name='option', value=str(values[name]))
                        if not force_value:
                            assert len(option) > 0, '0 select options found with the value %s' % values[name]
                            assert len(option) == 1, 'More than one select option found with the value %s' % values[name]
                        body.append((name, str(values[name])))
                    else:
                        option = field.find_all(lambda t: t.name == 'option' and t.has_attr('selected'))
                        assert len(option) < 2, 'More than one pre-selected option'
                        if option:
                            body.append((name, option[0]['value']))
                        else:
                            body.append((name, ''))
                elif field.name == 'textarea':
                    if name in values:
                        body.append((name, str(values[name])))
                    else:
                        body.append((name, field.string))
            method = form['method'] if form.has_attr('method') else 'GET'
            action = form['action'] if form.has_attr('action') else ''
            self.goto(action, method=method, params=body, **kwargs)
        else:
            assert False, 'No request sent'        

    def follow_redirect(self, **kwargs):
        """Follows a redirect specified in the current response."""
        if self._response:
            self._response = self._response.follow(**kwargs)
        else:
            assert False, 'No request sent'        
        
    def has_text(self, text):
        """Check whether the last response contains the given ``text``.

        :param text: The text to look for
        :type text: ``unicode``
        """
        if self._response:
            assert text in self._response.text, '"%s" not found in %s' % (text, self._response.text)
        else:
            assert False, 'No request sent'

    def has_status(self, status):
        if self._response:
            assert self._response.status_int == status,\
                'Response status is %s instead of %s' % (self._response.status_int, status)
        else:
            assert False, 'No request sent'


@pytest.yield_fixture
def pyramid_app_tester(app):
    """Fixture that provides a :class:`~pywebtools.testing.PyramidAppTester`.
    """
    tester = PyramidAppTester(app)
    yield tester
