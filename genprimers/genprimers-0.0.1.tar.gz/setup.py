from setuptools import find_packages, setup
import os


def get_readme():
    readme = ''
    try:
        import pypandoc
        readme = pypandoc.convert('Readme.md', 'rst')
    except (ImportError, IOError):
        with open('Readme.md', 'r') as file_data:
            readme = file_data.read()
    return readme


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

extra_files = package_files('lib/templates')
extra_files = ["/".join(elm.strip("/").split('/')[1:]) for elm in extra_files]

setup(
    name='genprimers',
    version='0.0.1',
    author='Diego Diaz Dominguez',
    author_email='ddiaz@dim.uchile.cl',
    description=('A software to design PCR primers for a a subset of ' +
                 ' sequences which belong to a greater set'),
    long_description=get_readme(),
    license='BSD',
    keywords='PCR primers designer',
    url='https://bitbucket.org/lbmg/genprimers',
    packages=find_packages(),
    package_data={'lib': extra_files},
    install_requires=['biopython==1.68',
                      'primer3-py==0.5.1',
                      'plotly==2.0.2',
                      'Jinja2==2.9.5'],
    entry_points={
        'console_scripts': ['genprimers=lib.genprimers:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics'
    ]
)
