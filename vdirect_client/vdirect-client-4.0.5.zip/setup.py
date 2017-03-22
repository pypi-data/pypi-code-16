from setuptools import setup,find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='vdirect-client',
    # Example: 3.41.0
    version='4.0.5',
    description='An unofficial auto generated REST based vDirect client',
    long_description=read('README.rst'),
    author='Avishay Balderman',
    author_email='avishayb@radware.com',
    py_modules=['vdirect_client'],
    license='MIT',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ]
)