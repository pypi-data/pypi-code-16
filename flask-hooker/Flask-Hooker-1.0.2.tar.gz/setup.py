"""
Flask-Hooker
--------------
"""

from setuptools import setup

setup(
    name='Flask-Hooker',
    version="1.0.2",
    url='http://github.com/doblel/Flask-Hooker/',
    license='MIT',
    author='Lisandro Lucatti (doblel)',
    author_email='lucattilisandro@gmail.com',
    description='Receive and manage webhooks of several services at the same time',
    long_description='',
    packages=['flask_hooker'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={},
    install_requires=['Flask'],
    tests_require=[
        'coverage'
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
