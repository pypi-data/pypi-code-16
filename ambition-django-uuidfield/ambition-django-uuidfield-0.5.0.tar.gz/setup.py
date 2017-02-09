from setuptools import setup, find_packages

setup(
    name='ambition-django-uuidfield',
    version='0.5.0',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    description='Ambition fork of dcramer/django-uuidfield, UUIDField in Django',
    url='https://github.com/ambitioninc/django-uuidfield',
    zip_safe=False,
    install_requires=[
        'django',
        'six',
    ],
    tests_require=[
        'psycopg2',
        'django-nose',
    ],
    packages=find_packages(),
    test_suite='runtests.runtests',
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
