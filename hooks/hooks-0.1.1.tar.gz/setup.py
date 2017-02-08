import setuptools

install_requires = open('requirements.txt').readlines()

setuptools.setup(
    name="hooks",
    version="0.1.1",
    url="https://github.com/kevinjqiu/githooks",

    author="Kevin Jing Qiu",
    author_email="kevin@idempotent.ca",

    description="Convenient git hooks",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=install_requires,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    entry_points={
        'console_scripts': [
            'hooks=hooks.main:cli',
        ]
    },
)
