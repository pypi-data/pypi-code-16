from setuptools import setup, find_packages

setup(
    name='simc-autobahn',
    version='1.0.1',
    packages=find_packages(),
    description='A SimC microservice build with Crossbar.io/ Autobahn',
    url='https://gitlab.com/simc/simc-autobahn',
    author='endymonium',
    author_email='endymonium@gmail.com',
    license='GNU GPLv3 ',
    install_requires=['autobahn', 'docopt', 'bs4', 'requests', 'yattag', 'peewee'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'foo = start'
        ]
    }
)
