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
        name = 'succubus',
        version = '1.0-56',
        description = 'Lightweight Python module for daemonizing',
        long_description = '.. image:: https://travis-ci.org/ImmobilienScout24/succubus.svg\n    :alt: Travis build status image\n    :align: left\n    :target: https://travis-ci.org/ImmobilienScout24/succubus\n\n.. image:: https://coveralls.io/repos/ImmobilienScout24/succubus/badge.svg?branch=master\n  :alt: Coverage status\n  :target: https://coveralls.io/github/ImmobilienScout24/succubus?branch=master\n\n\n========\nsuccubus\n========\n\nDescription\n===========\nsuccubus is a lightweight python module for a fast and easy creation of\npython daemons and init scripts.\n\nExamples\n========\n\n.. code-block:: python\n\n    #!/usr/bin/env python\n\n    import logging\n    import sys\n    import time\n\n    from logging.handlers import WatchedFileHandler\n\n    from succubus import Daemon\n\n\n    class MyDaemon(Daemon):\n        def run(self):\n            """Overwrite the run function of the Daemon class"""\n            # TODO: don\'t log to /tmp except for example code\n            handler = WatchedFileHandler(\'/tmp/succubus.log\')\n            self.logger = logging.getLogger(\'succubus\')\n            self.logger.addHandler(handler)\n            while True:\n                time.sleep(1)\n                self.logger.warn(\'Hello world\')\n\n\n    def main():\n        daemon = MyDaemon(pid_file=\'succubus.pid\')\n        sys.exit(daemon.action())\n\n\n    if __name__ == \'__main__\':\n        main()\n        \nSuccubus implements the usual init script actions (start, stop, restart, status) in Python. So your init script can look like this:\n        \n.. code-block:: bash\n\n    #!/bin/bash\n    /usr/bin/my_succubus_daemon $1 --foo=42\n\nIf the init script is called as ``/etc/init.d/my_succubus_daemon start``, this will translate into ``/usr/bin/my_succubus_daemon start --foo=42`` being called. The ``start`` parameter is consumed by the succubus framework, i.e. when your code does the command line parsing, it looks as if ``/usr/bin/my_succubus_daemon --foo=42`` was called. You can now parse the ``--foo=42`` parameter as you please.\n',
        author = 'Stefan Neben, Stefan Nordhausen',
        author_email = 'stefan.neben@immobilienscout24.de, stefan.nordhausen@immobilienscout24.de',
        license = 'Apache License 2.0',
        url = 'https://github.com/ImmobilienScout24/succubus',
        scripts = [],
        packages = ['succubus'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = ['psutil'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
