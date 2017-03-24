from distutils.core import setup

# Read the version number
with open("columnar_records/_version.py") as f:
    exec(f.read())

setup(
    name='columnar_records',
    version=__version__, # use the same version that's in _version.py
    author='David N. Mashburn',
    author_email='david.n.mashburn@gmail.com',
    packages=['columnar_records'],
    scripts=[],
    url='http://pypi.python.org/pypi/columnar_records/',
    license='LICENSE.txt',
    description='A dataframe-like object but simpler (basically a list of numpy arrays on steroids)',
    long_description=open('README.md').read(),
    install_requires=[
                      'numpy>=1.0',
                      'future>=0.16',
                     ],
)
