from setuptools import setup

setup(
        name='redskyAPI',
        version='1.0.6-1',
        description='Client API for the redsky.fr chat',
        url='http://beerstorm.info/redskyAPI',
        author='Beerstorm',
        author_email='beerstorm.emberbeard@gmail.com',
        license='GPLv3',
        packages=['redskyAPI'],
        install_requires=[
            'requests',
            'socketIO_client',
            ],
        zip_safe=False,
        )
