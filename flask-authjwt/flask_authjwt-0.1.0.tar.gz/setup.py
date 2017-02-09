"""Config file."""

from setuptools import setup

setup(
    name='flask_authjwt',
    version='0.1.0',
    description='Module to secure flask endpoints in appengine using jwt token.',
    url='https://github.laureate.net/Laureate/flask_authjwt',
    author='Handerson Contreras',
    author_email='handerson.contreras@gmail.com',
    license='MIT',
    packages=['flask_authjwt'],
    install_requires=['PyJWT', 'flask', 'Flask-RESTful==0.3.4'],
    zip_safe=False
)
