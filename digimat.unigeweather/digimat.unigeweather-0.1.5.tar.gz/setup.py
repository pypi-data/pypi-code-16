from setuptools import setup, find_packages

setup(
    name='digimat.unigeweather',
    version='0.1.5',
    description='Digimat UNIGE weather data access',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@st-sa.ch',
    url='http://www.digimat.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
