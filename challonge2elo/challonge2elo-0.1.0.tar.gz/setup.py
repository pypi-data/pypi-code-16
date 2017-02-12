from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='challonge2elo',
    version='0.1.0',
    description='Elo ratings from Challonge tournament results.',
    long_description=readme,
    author='Matthew Gray',
    url='https://github.com/mtgray/challonge2elo',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'challonge2elo=challonge2elo:main'
        ]
    },
    install_requires=[
        'docopt',
        'elo',
        'requests'
    ]
)
