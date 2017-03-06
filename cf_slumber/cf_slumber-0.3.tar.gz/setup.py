from setuptools import setup

setup(
    name='cf_slumber',
    py_modules=['cf_slumber'],
    version='0.3',
    description='CloudFoundry client based on Slumber',
    author='Soren Hansen',
    author_email='soren@linux2go.dk',
    url='https://github.com/sorenh/cf_slumber',
    install_requires=[
        'slumber',
        'requests_oauthlib'
    ],
    tests_require=['six',
                   'requests-mock'],
)
