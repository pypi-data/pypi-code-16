import os
import sys
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages

overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "openedoo-test"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break

setup (
    name='openedoo',
    version='0.2.5',
    url='http://openedoo.org',
    author='rendiya',
    author_email='ligerrendy@gmail.com',
    description=('open source platform for education.'),
    license='MIT',
    packages=find_packages(),
    package_dir={'openedoo_core':'openedoo_core'},
    include_package_data=True,
    scripts=['openedoo_core/manage.py'],
    install_requires=[
	   'flask',
       'openedoo-script-test',
       'sqlalchemy',
       'MySQL-python',
       'redis',
       'Werkzeug',
       'itsdangerous',
       'click',
       'Jinja2',
       'alembic',
       'flask-migrate',
       'Flask-Script',
       'GitPython',
       'gitdb2',
       'smmap2'
	],
    entry_points={'console_scripts': [
        'openedoo = openedoo_core.command:main',
    ]},
    zip_safe = False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

if overlay_warning:
    sys.stderr.write("""
========
WARNING!
========
You have just installed openedoo-test over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
openedoo-test. This is known to cause a variety of problems. You
should manually remove the
%(existing_path)s
directory and re-install openedoo-test.
""" % {"existing_path": existing_path})
