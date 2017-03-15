from setuptools import setup, find_packages
import os


version = '0.6.0.post1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'angular_xeditable', 'test_angular-xeditable.txt')
    + '\n' +
    read('CHANGES.rst'))


setup(
    name='js.angular_xeditable',
    version=version,
    description="Fanstatic packaging of Angular-xeditable",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Fanstatic Developers',
    author_email='fanstatic@googlegroups.com',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.angular',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'angular-xeditable = js.angular_xeditable:library',
            ],
        },
    )
