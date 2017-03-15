import sys

from setuptools import setup

if sys.version_info >= (3, 4):
    install_requires = ["fabric3==1.12.post1"]
else:
    install_requires = ["fabric==1.12.0"]

install_requires += ['click==6.6']

setup(
    name='django-deployment-sm',
    version="0.2.6",
    packages=['classes'],
    scripts=['django-deploy'],
    install_requires=install_requires,
    zip_safe=False,
)
