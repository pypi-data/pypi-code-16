from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()
        
setup(name='isight',
      version='0.7',
      description='Library to submit queries to iSIGHT API and return the result back',
      url='https://github.com/maltantawy/iSIGHT-api',
      author='Mostafa Altantawy',
      author_email='mostafa.altantawy@gmail.com',
      license='GPL',
      packages=['isight'],
      include_package_data=True,
      zip_safe=False)
