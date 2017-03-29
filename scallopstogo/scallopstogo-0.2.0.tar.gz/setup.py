from setuptools import setup, find_packages

DESCRIPTION = (
    '''
    Python library of helper and connection functions for use with
    Google Calendar API
    '''
)

setup(
    name="scallopstogo",
    version="0.2.0",
    author="Andrew Lee",
    author_email="andrewlee@indeed.com",
    license="Reserved",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'pandas',
        'pytz',
        'httplib2',
        'oauth2client'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
