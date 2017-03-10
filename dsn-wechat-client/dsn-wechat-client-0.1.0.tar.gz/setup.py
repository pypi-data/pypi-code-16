from setuptools import setup, find_packages

version = '0.1.0'

setup(
    name="dsn-wechat-client",
    version=version,
    packages=find_packages(exclude=['test']),
    install_requires=[
        'setuptools',
        'requests>=2.13.0'
    ],
    zip_safe=False,
    author=['desean'],
    author_email=['desean66@outlook.com'],
    license='MIT',
    url='https://github.com/desean/wechat-client',
    description='python client for wechat',
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
