from distutils.core import setup
from image4layer import __version__

long_description = open("README.txt").read()

setup(
    name='Image4Layer',
    version=__version__,
    packages=['image4layer'],
    package_dir={'image4layer': 'image4layer'},
    url='https://github.com/pashango2/Image4Layer',
    license='MIT',
    author='Toshiyuki Ishii',
    author_email='pashango2@gmail.com',
    description="It is implemented by 'pillow' in blend mode of CSS3. And more...",
    long_description=long_description,
)
