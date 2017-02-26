#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'karellen-geventws',
        version = '1.0.2',
        description = 'Karellen Gevent Websocket Library',
        long_description = 'Karellen Gevent Websocket Library\n=================================\n\n|Gitter chat|\n\nThis is a `Karellen <https://www.karellen.co/karellen/>`__ fork of\n`gevent-websocket <http://www.bitbucket.org/Jeffrey/gevent-websocket/>`__.\nThe goal of this fork is to maintain the project to support Python 3.3,\n3.4 and 3.5+ as well as latest WS standards errata.\n\n`karellen-geventws <https://github.com/karellen/karellen-geventws/>`__\nis a WebSocket library for the `gevent <http://www.gevent.org/>`__\nnetworking library.\n\nFeatures include:\n\n-  Integration on both socket level or using an abstract interface.\n-  RPC and PubSub framework using `WAMP <http://wamp-proto.org>`__\n   (WebSocket Application Messaging Protocol).\n-  Easily extendible using a simple WebSocket protocol plugin API\n\n.. code:: python\n\n\n        from geventwebsocket import WebSocketServer, WebSocketApplication, Resource\n\n        class EchoApplication(WebSocketApplication):\n            def on_open(self):\n                print("Connection opened")\n\n            def on_message(self, message):\n                self.ws.send(message)\n\n            def on_close(self, reason):\n                print(reason)\n\n        WebSocketServer(\n            (\'\', 8000),\n            Resource({\'/\': EchoApplication})\n        ).serve_forever()\n\nor a low level implementation:\n\n.. code:: python\n\n\n        from gevent import pywsgi\n        from geventwebsocket.handler import WebSocketHandler\n\n        def websocket_app(environ, start_response):\n            if environ["PATH_INFO"] == \'/echo\':\n                ws = environ["wsgi.websocket"]\n                message = ws.receive()\n                ws.send(message)\n\n        server = pywsgi.WSGIServer(("", 8000), websocket_app,\n            handler_class=WebSocketHandler)\n        server.serve_forever()\n\nMore examples can be found in the ``src/unittest/python`` directory.\nHopefully more documentation will be available soon.\n\nInstallation\n============\n\nThe easiest way to install karellen-geventws is directly from\n`PyPi <https://pypi.python.org/pypi/karellen-geventws/>`__ using pip or\nsetuptools by running the commands below:\n\n::\n\n    $ pip install karellen-geventws\n\nGunicorn Worker\n---------------\n\nUsing Gunicorn it is even more easy to start a server. Only the\nwebsocket\\_app from the previous example is required to start the\nserver. Start Gunicorn using the following command and worker class to\nenable WebSocket funtionality for the application.\n\n::\n\n    gunicorn -k "geventwebsocket.gunicorn.workers.GeventWebSocketWorker" wsgi:websocket_app\n\nPerformance\n-----------\n\n`karellen-geventws <https://github.com/karellen/karellen-geventws/>`__\nis pretty fast, but can be accelerated further by installing\n`wsaccel <https://github.com/methane/wsaccel>`__ and ``ujson`` or\n``simplejson``:\n\n::\n\n    $ pip install wsaccel ujson\n\n`karellen-geventws <https://github.com/karellen/karellen-geventws/>`__\nautomatically detects ``wsaccel`` and uses the Cython implementation for\nUTF8 validation and later also frame masking and demasking.\n\nGet in touch\n------------\n\nThe fork parent is located at\n`gevent-websocket <http://www.bitbucket.org/Jeffrey/gevent-websocket/>`__.\n\nIssues can be created on\n`GitHub <https://github.com/karellen/karellen-geventws/issues>`__.\n\n.. |Gitter chat| image:: https://badges.gitter.im/karellen/gitter.svg\n   :target: https://gitter.im/karellen/lobby\n',
        author = 'Jeffrey Gelens, Karellen, Inc',
        author_email = 'jeffrey@noppo.pro, supervisor@karellen.co',
        license = 'Apache License, Version 2.0',
        url = 'https://github.com/karellen/karellen-geventws',
        scripts = [],
        packages = [
            'geventwebsocket',
            'geventwebsocket.gunicorn',
            'geventwebsocket.protocols'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['gevent'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '<3.7,>=3.3',
        obsoletes = [],
    )
