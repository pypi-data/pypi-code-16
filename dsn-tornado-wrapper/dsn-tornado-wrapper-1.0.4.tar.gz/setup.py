from setuptools import setup, find_packages

version = '1.0.4'

setup(
    name="dsn-tornado-wrapper",
    version=version,
    packages=find_packages(exclude=['demo', 'test']),
    install_requires=[
        'setuptools',
        'tornado>=4.4.2',
        'dsn-redis-wrapper>=1.0.3',
    ],
    zip_safe=False,
    author=['desean'],
    author_email=['desean66@outlook.com'],
    license='MIT',
    url='https://github.com/desean/tornado-wrapper',
    description='A simple and lightweight wrapper for tornado',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
