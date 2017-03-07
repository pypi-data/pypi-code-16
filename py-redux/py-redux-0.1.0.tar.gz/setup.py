from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README'), 'r') as f:
    long_description = f.read()

setup(
    name="py-redux",
    version="0.1.0",
    description="python implementation of the redux library",
    long_description=long_description,
    url='https://github.com/emersondispatch/pyredux',
    author='Emerson Knapp',
    author_email='emerson@dispatch.ai',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='redux development state ui',
    packages=['redux'],
    install_requires=['frozendict'],
)
