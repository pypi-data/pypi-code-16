from setuptools import setup, find_packages

name = 'inouk.edofx'
version = '0.3.9'


long_description = (
    '\nDetailed Documentation\n'
      '######################\n'
    + '\n' +
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '############\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    'Change history\n'
    '##############\n'
    + '\n' +
    open('CHANGES.txt').read()
    + '\n'
)

setup(
    name = name,
    version = version,
    packages = find_packages('src'),
    namespace_packages = ['inouk'],
    package_dir={'': 'src'},
    url='https://github.com/cmorisse/inouk.edofx',
    license='MIT',
    author='Cyril MORISSE',
    author_email='cmorisse@boxes3.net',
    description='A framework to read and write OFX files Version 1.',
    long_description = long_description,
    keywords = "ofx",
    include_package_data=True,
    #install_requires=['setuptools',],
    classifiers=[
        #'Framework :: Buildout',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Markup :: SGML',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Natural Language :: English',
     ],

)
