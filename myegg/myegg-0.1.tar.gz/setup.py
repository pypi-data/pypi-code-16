from setuptools import setup


def readme():
    with open('README') as f:
        return f.read()


setup(name='myegg',
      version='0.1',
      description='The hello world from myegg ',
      long_description=readme(),
      keywords='myegg egg hello world',
      url='https://github.com/huaqiangli/myegg',
      author='Huaqiang Li',
      author_email='huaqiangli@hotmail.com',
      license='MIT',
      packages=['myegg'],
      install_requires=[
          'argparse',
      ],
      entry_points={
          'console_scripts': ['myegg=myegg.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)
