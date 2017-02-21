from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name="linked_list",
    version="0.0.7",
    description="Classes for linked lists and doubly linked lists",
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'      
    ],
    keywords='linked list data structure',
    url="https://github.com/jakab922/linked_list",
    download_url="https://github.com/jakab922/linked_list/tarball/0.0.7",
    author="Daniel Papp",
    author_email="jakab922@gmail.com",
    license="MIT",
    packages=["linked_list"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
    zip_safe=False
)
