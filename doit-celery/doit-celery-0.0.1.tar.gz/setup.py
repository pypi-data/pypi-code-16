from setuptools import setup
from os.path import join, dirname

with open(join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(
    name="doit-celery",
    version="0.0.1",
    description="An async task framework basecd on celery",
    long_description=__doc__,
    author="Wang Feng (Felix)",
    author_email='wangfelix87@gmail.com',
    url="",
    packages=["doit"],
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
