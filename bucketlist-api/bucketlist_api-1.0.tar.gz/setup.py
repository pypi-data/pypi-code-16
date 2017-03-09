from setuptools import setup

setup(
    name='bucketlist_api',
    description='A RESTful api for an online bucketlist service',
    url='https://github.com/giddygitau/bucketlist',
    download_url='https://github.com/giddygitau/bucketlist/archive/1.0.tar.gz',
    author='Gideon Gitau',
    author_email='nggitau@gmail.com',
    license='MIT',
    packages=['bucketlist_api'],
    install_requires=[
        'flask',
        'faker',
        'flask-restful',
        'flask-bcrypt',
        'flask-jwt',
        'flask-migrate',
        'flask-script',
        'flask-sqlalchemy'
    ],
    version='1.0',
    include_package_data=True,
    zipsafe=False,
    test_suite='nose.collector',
    test_require=['nose']
)
