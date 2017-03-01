from setuptools import setup, find_packages

EXCLUDE_FROM_PACKAGES = ['openedoo.template.project_template',
                         'openedoo.template.module_template',
                         'openedoo.bin']

setup (
    name='openedoo-cli-test',
    version='1.0.1.1',
    install_requires=[
	   'flask',
       'flask-script',
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
    license='MIT',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    scripts=['openedoo/bin/openedoo.py'],
    entry_points={'console_scripts': [
        'openedoo = openedoo.core.management:openedoo_cli',
    ]},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
