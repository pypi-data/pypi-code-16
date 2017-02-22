from setuptools import setup, find_packages

setup(
    name='cryptox',
    version='0.2.0',
    description = 'Python module for cryptocurrency analysis and trading',
    url='https://bitbucket.org/blevine11/cryptox',
    author='Benjamin Levine',
    author_email='benjamin.r.levine@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='cryptocurrency exchange module',
    packages = find_packages(),
    install_requires=['requests']
)