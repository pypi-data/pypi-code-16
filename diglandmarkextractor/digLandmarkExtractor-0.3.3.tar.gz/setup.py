try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'name': 'digLandmarkExtractor',
    'description': 'digLandmarkExtractor',
    'author': 'Jason Slepicka',
    'url': 'https://github.com/usc-isi-i2/dig-landmark-extractor',
    'download_url': 'https://github.com/usc-isi-i2/dig-landmark-extractor',
    'author_email': 'jasonslepicka@gmail.com',
    'version': '0.3.3',
    'install_requires': ['landmark_extractor', 'digExtractor>=0.3.2'],
    # these are the subdirs of the current directory that we care about
    'packages': ['digLandmarkExtractor'],
    'scripts': [],
}

setup(**config)
