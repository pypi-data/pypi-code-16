from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='valid_email',
      version='0.4',
      description='Package to find a valid email id.',
      long_description=readme(),
      url='https://github.com/hmnhGeek/valid_email',
      author='Himanshu Sharma',
      author_email='hmnhsharma97@gmail.com',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
