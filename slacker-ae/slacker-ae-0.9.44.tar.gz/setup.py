from setuptools import setup


setup(
    name='slacker-ae',
    version='0.9.44',
    packages=['slacker'],
    description='Slack API client (App Engine)',
    author='Bao Le',
    author_email='leducbao@gmail.com',
    url='http://github.com/baole/slacker/',
    # install_requires=['requests >= 2.2.1'],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='slack api'
)
