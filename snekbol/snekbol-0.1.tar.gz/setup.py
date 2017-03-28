from distutils.core import setup


setup(
    name = 'snekbol',
    packages = ['snekbol'],
    version = '0.1',
    description = 'A python based library for reading and writing SBOL 2 files',
    author = 'Thomas Craig',
    author_email = 'thomas.craig@tjc.me.uk',
    url = 'https://github.com/tjomasc/snekbol',
    keywords = ['SBOL', 'Synthetic Biology'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
