from setuptools import setup


config = {
    'name': 'rwtfoms',
    'version': '0.0.1',
    'description': 'WTForms support for Rueckenwind',
    'author': 'Florian Ludwig',
    'url': '',
    'author_email': 'f.ludwig@greyrook.com',
    'install_requires': ['wtforms', 'rueckenwind'],
    'packages': ['rwtforms'],
    'scripts': [],
}

setup(**config)
