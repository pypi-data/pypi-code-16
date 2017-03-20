from setuptools import setup

setup(
    name='django-pgconninfo',
    version='0.9',
    description='PostgreSQL connection info from invironment variables',
    url='http://github.com/ihabhussein/django-pgconninfo',
    author='Ihab Hussein',
    author_email='ihab@ihabhussein.com',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
    ],
    keywords='PostgreSQL connection',
    packages=['pgconninfo'],
    install_requires=[
        "pgpasslib >= 1.1.0",
    ],
    zip_safe=True
)
