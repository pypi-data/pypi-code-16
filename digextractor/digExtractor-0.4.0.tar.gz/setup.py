try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'digExtractor',
    'description': 'digExtractor',
    'author': 'Jason Slepicka',
    'url': 'https://github.com/usc-isi-i2/dig-extractor',
    'download_url': 'https://github.com/usc-isi-i2/dig-extractor',
    'author_email': 'jasonslepicka@gmail.com',
    'version': '0.4.0',
    'packages': ['digExtractor'],
    'scripts': [],
    'install_requires':['jsonpath-rw>=1.4.0', 'jsonpath-rw-ext>=1.0.0']
}

setup(**config)
