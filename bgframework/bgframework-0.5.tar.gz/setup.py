from setuptools import setup, find_packages
from bgframework import __version__
# from Cython.Build import cythonize

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Communications',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
    'Topic :: Internet :: WWW/HTTP :: Site Management',
    'Programming Language :: Python :: 3.4',
]

config = {
    'name': 'bgframework',
    'description': 'Django background management full-stack framework',
    'long_description': "Django background management full-stack framework",
    'url': 'https://github.com/tkliuxing/bgframework',
    'author': 'Ronald White',
    'author_email': 'ouyanghongyu@gmail.com',
    'license': 'Apache License 2.0',
    'version': __version__,
    'install_requires': [
        'Django<1.10',
        'django-braces==1.9.0',
        'django-sekizai==0.9.0',
        'django-bootstrap-form-tkliuxing==3.2.1',
        'six==1.10.0',
    ],
    'setup_requires': [
        'setuptools_scm'
    ],
    'packages': find_packages(),
    'include_package_data': True,
    'platforms': ['OS Independent'],
    'scripts': [],
    'zip_safe': False,
    'classifiers': CLASSIFIERS,
    # 'ext_modules': cythonize([Extension("helloworld", ["helloworld.pyx"]),]),
}

setup(**config)
