from distutils.core import setup
from setuptools import find_packages

version = '1.0.1'
setup(
    name='nlpbox',
    version=version,
    author='Wu Zhen Zhou',
    author_email='hyciswu@gmail.com',
    install_requires=['numpy>=1.7.1',
                      'six>=1.9.0',
                      'scikit-learn>=0.17',
                      'pandas>=0.17',
                      'scipy>=0.17'],
    url='https://github.com/hycis/NLPBox',
    download_url = 'https://github.com/hycis/NLPBox/tarball/{}'.format(version),
    license='Apache 2.0, see LICENCE',
    description='a nlpbox toolbox',
    long_description=open('README.md').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True
)
