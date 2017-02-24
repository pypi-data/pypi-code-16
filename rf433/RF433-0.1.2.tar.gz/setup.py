
import RF433
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='RF433',
    packages=find_packages(),
    version=RF433.__version__,
    description='RF433 library to send signals for various protocols using \
                    an arduino',
    author='Bruno Silva',
    author_email='brunomiguelsilva@ua.pt',
    url='https://github.com/bsilvr/pyRF433',
    include_package_data=True,
    # download_url='https://github.com/bsilvr/pyRF433/tarball/0.1.2',
    keywords=['rf433', 'arduino'],
    license='LICENSE',
    classifiers=[],
    install_requires=[
       'pyserial==3.1.1'
    ]
)
