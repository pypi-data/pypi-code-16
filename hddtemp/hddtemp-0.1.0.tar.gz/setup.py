from setuptools import setup

hddtemp_classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',
]

setup(
    name='hddtemp',
    description='An hddtemp client',
    version='0.1.0',
    license='GPLv3+',
    author='Dennis Fink',
    author_email='dennis.fink@c3l.lu',
    py_modules=['hddtemp'],
    platforms='any',
    classifiers=hddtemp_classifiers,
)
