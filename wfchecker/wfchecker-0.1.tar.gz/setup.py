from setuptools import setup


setup(
    name='wfchecker',
    version='0.1',
    description='Extracts javascript code from a json file and checks it for syntax errors.',
    url='https://bitbucket.org/longedok/wf_checker',
    author='Evgeniy Kartavkyh',
    author_email='longedok@gmail.com',
    license='MIT',
    packages=['wfchecker'],
    zip_safe=False,
    entry_points = {
        'console_scripts': ['wfchecker=wfchecker.wf_checker:main']
    }
)

