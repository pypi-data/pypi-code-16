from setuptools import find_packages,setup

setup(
    description='Viking Makt Framework',
    install_requires=[
        'pika',
        'tornado',
        'simplejson',
        'colorlog',
        'bencode',
        'arrow',
        'pdbpp'
    ],
    license='http://code.umgeher.org/fossil.cgi/rask/artifact/3b9a146264aed1f5',
    maintainer='Umgeher Torgersen',
    maintainer_email='me@umgeher.org',
    name='rask',
    packages=find_packages(),
    url='http://code.umgeher.org/rask',
    version="0.1.0"
)
