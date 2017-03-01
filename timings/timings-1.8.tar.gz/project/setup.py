from setuptools import setup, find_packages

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='timings',
      version='1.8',
      description='Convert time from seconds.',
      author='Himanshu Sharma',
      license='MIT',
      packages=find_packages(),

      include_package_data=True,
      zip_safe=False,
      entry_points = {
        'console_scripts': ['timings-run=timings.command_line:main']})
