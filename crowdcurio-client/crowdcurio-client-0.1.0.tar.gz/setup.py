from setuptools import setup, find_packages

setup(
    name='crowdcurio-client',
    url='https://github.com/crowdcurio/crowdcurio-client',
    author='Alex Williams',
    author_email='alex.williams@uwaterloo.ca',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    keywords='crowdcurio',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'requests>=2.4.2',
    ],
)
