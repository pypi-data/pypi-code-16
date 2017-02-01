# -*- coding: utf-8 -*-
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Extra functionality for Flask logging

Flask-Logging-Extras is a Flask extension that plugs into the logging
mechanism of Flask applications.

Flask-Logging-Extras requires you to set FLASK_LOGGING_EXTRAS_KEYWORDS to a
dictionary value, where the dictionary key is a the key you can use in the
log message format, and the value is a default value that is substituted if
no value is present in the message record.
"""

import logging

__version_info__ = ('0', '0', '1')
__version__ = '.'.join(__version_info__)
__author__ = 'Gergely Polonkai'
__license__ = 'MIT'
__copyright__ = '(c) 2015 GT2'

class FlaskExtraLogger(logging.getLoggerClass()):
    """
    A logger class that is capable of adding extra keywords to log formatters

    Usage:

    .. code-block:: python

       import logging

       from flask_logging_extras import register_logger_class

       # This must be done before the app is initialized!
       register_logger_class(cls=FlaskExtraLogger)

       app = Flask(__name__)
       app.config['FLASK_LOGGING_EXTRAS_KEYWORDS'] = {'category': '<unset>'}
       app.logger.init_app()

       formatter = logging.Formatter(
           '[%(asctime)s] [%(levelname)s] [%(category)s] %(message)s')
       handler = logging.FileHandler('app.log', mode='a')
       handler.setFormatter(formatter)
       handler.setLevel(logging.INFO)

       app.logger.addHandler(handler)

       app.logger.info('The message', category='my category')

       # This will produce something like this in app.log:
       # [TIMESTAMP2017-01-16 08:44:48.944] [INFO] [my category] The message
    """

    def __init__(self, *args, **kwargs):
        if 'app' in kwargs:
            if kwargs['app'] is not None:
                raise TypeError(
                    "Cannot initialise {classname} with an app.  See the"
                    "documentation of Flask-Logging-Extras for more info."
                    .format(classname=self.__class__.__name__))
            else:
                # If app is None, treat it as if it wasn’t there
                del(kwargs['app'])

        self.app = None
        self._valid_keywords = []

        super(FlaskExtraLogger, self).__init__(*args, **kwargs)

    def _log(self, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}

        for kw in self._valid_keywords:
            if kw in kwargs:
                kwargs['extra'][kw] = kwargs[kw]
                del(kwargs[kw])
            else:
                kwargs['extra'][kw] = self._valid_keywords[kw]

        super(FlaskExtraLogger, self)._log(*args, **kwargs)

    def init_app(self, app):
        """
        Intialize the logger class with a Flask application

        The class reads its necessary configuration from the config of this
        application.

        If the application doesn’t call this, or doesn’t have the
        `FLASK_LOGGING_EXTRAS_KEYWORDS` in its config, no extra
        functionality will be added.

        :param app: a Flask application
        :type app: Flask
        :raises ValueError: if the app tries to register a keyword that is
                             reserved for internal use
        """

        app.config.setdefault('FLASK_LOGGING_EXTRAS_KEYWORDS', {})

        for kw in app.config['FLASK_LOGGING_EXTRAS_KEYWORDS']:
            if kw in ['exc_info', 'extra', 'stack_info']:
                raise ValueError(
                    '"{keyword}" member of FLASK_LOGGING_EXTRAS_KEYWORDS is '
                    'reserved for internal use.')

        self._valid_keywords = app.config['FLASK_LOGGING_EXTRAS_KEYWORDS']


def register_logger_class(cls=FlaskExtraLogger):
    """
    Register a new logger class

    It is effectively a wrapper around `logging.setLoggerClass()`, with an
    added check to make sure the class can be used as a logger.

    To use the extra features of the logger class in a Flask app, you must
    call it before the app is instantiated.

    This function returns the logger class that was the default before
    calling.  This might be useful if you only want to use `cls` in the
    Flask app object, but not anywhere else in your code.  In this case,
    simply call `register_logger_class()` again with the return value from
    the first invocation.

    :param cls: a logger class to register as the default one
    :type cls: class(logging.Logger)
    :returns: the old default logger class
    :rtype: class
    :raises TypeError: if the class is not a subclass of `logging.Logger`
    """

    if not issubclass(cls, logging.Logger):
        raise TypeError(
            "The logger class must be a subclass of logging.Logger!")

    old_class = logging.getLoggerClass()
    logging.setLoggerClass(cls)

    return old_class
