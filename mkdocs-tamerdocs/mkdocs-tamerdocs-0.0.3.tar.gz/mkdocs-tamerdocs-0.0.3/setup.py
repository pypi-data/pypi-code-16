from setuptools import setup, find_packages

VERSION='0.0.3'


setup(
    name="mkdocs-tamerdocs",
    version=VERSION,
    url='https://anantshri.github.io/mkdocs-tamerdocs/',
    license='GPL',
    description='Mkdocs theme used on AndroidTamer Documentation portals',
    author='Anant Shrivastava',
    author_email='anant@anantshri.info',
    keywords = [ 'mkdocs','documentation','theme'], # 
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes':[
            'tamerdocs=tamerdocs',
        ]
    },
    zip_safe=False
)