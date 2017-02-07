from setuptools import setup

setup(
    name='django_logger',
    version='0.1.1.0',
    packages=['django_logger'],
    requires=['python (>= 2.5)', 'django (>= 1.3)'],
    description='django_logger',
    long_description=open('README.rst').read(),
    author='ChaosHead',
    author_email='prostomrkot@gmail.com',
    license='MIT License',
    keywords='django',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
