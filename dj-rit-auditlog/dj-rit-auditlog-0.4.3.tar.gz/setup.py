from distutils.core import setup

setup(
    name='dj-rit-auditlog',
    version='0.4.3',
    packages=['auditlog', 'auditlog.migrations'],
    package_dir={'': 'src'},
    url='https://github.com/audiolion/dj-rit-auditlog',
    license='MIT',
    author='Jan-Jelle Kester, Ryan Castner',
    description='Audit log app for Django',
    install_requires=[
        'Django>=1.8',
        'django-jsonfield>=1.0.0',
    ],
    zip_safe=False
)
