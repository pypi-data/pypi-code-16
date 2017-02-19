from setuptools import setup

def readme():
        with open('py2oracle/README.rst') as f:
                return f.read()


setup(
        name='py2oracle',
        version='0.4',
        description='use py to read Oracle DB',
        #long_description='local test package',
        long_description=readme(),
        classifiers=[
                'Development Status :: 3 - Alpha',
                'License :: OSI Approved :: MIT License',
                'Programming Language :: Python :: 2.7'
        ],
        keywords='oracle db query',
        url='http://rkalva89828.kau.roche.com/gpa/py2oracle',
        author='Jian Dai',
        author_email='daij12@gene.com',
        license='MIT',
        packages=['py2oracle'],
        install_requires=[
                'JayDeBeApi',
                'JPype1'
        ],
        dependency_links=[], #Packages Not On PyPI
        include_package_data=True,
        test_suite='nose.collector',
        tests_require=['nose'],
        zip_safe=False)
