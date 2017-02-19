from setuptools import find_packages,setup

setup(
    description='Viking Makt Framework',
    install_requires=[
        'pika',
        'tornado',
        'simplejson',
        'colorlog',
        'bencode',
        'arrow'
    ],
    license='https://gitlab.com/vikingmakt/rask/raw/master/LICENSE',
    maintainer='Umgeher Torgersen',
    maintainer_email='me@umgeher.org',
    name='rask',
    packages=find_packages(),
    url='https://gitlab.com/vikingmakt/rask',
    version="0.0.109"
)
