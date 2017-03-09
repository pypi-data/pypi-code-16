import setuptools

setuptools.setup(
    name='remotemath',
    license='MIT',
    description="Math. Remote.",
    long_description="Math. Very remote.",
    use_incremental=True,
    setup_requires=['incremental'],
    author="Moshe Zadka",
    author_email="zadka.moshe@gmail.com",
    packages=setuptools.find_packages(where='src') + ['twisted.plugins'],
    package_dir={"": "src"},
    install_requires=['incremental', 'klein'],
)
