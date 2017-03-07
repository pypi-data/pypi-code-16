from setuptools import setup
import os.path


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        pass


setup(
    name='flake8-import-order-fuzeman',
    version='1.3.0',
    description="@fuzeman's import order style for flake8-import-order",
    long_description=readme(),
    url='https://github.com/fuzeman/flake8-import-order-fuzeman',
    author='Dean Gardiner',
    author_email='me@dgardiner.net',
    maintainer='Dean Gardiner',
    maintainer_email='me@dgardiner.net',
    license='GPLv3 or later',
    py_modules=['flake8_import_order_fuzeman'],
    install_requires=['flake8-import-order>=0.12'],
    entry_points='''
        [flake8_import_order.styles]
        fuzeman = flake8_import_order_fuzeman:Fuzeman
    ''',
    test_suite='flake8_import_order_fuzeman.TestCase',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ]
)
