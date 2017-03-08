from setuptools import find_packages, setup

setup(
    name='app-his-migrator',
    version='1.0.2',
    author='ODT',
    author_email='aajrf1992@gmail.com',
    description=('Este aplicativo se utiliza para migrar la informacion de atenciones al HIS MINSA'),
    long_description="",
    license='BSD',
    packages=find_packages(exclude=['config', 'testHis']),
    package_data={
        'starwars_ipsum': ['']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ]
)
