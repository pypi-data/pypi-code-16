from setuptools import setup

def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='topser',
      version='0.2',
      description='The simple package',
      long_description=readme(),
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.4',
            'Topic :: Text Processing :: Linguistic',
      ],
      url='http://github.com/vitakrya/topser',
      author='Vita Kr',
      author_email='vinder_2@mail.ru',
      license='MIT',
      packages=['topser'],
      install_requires=[
            'markdown',
      ],
      include_package_data=True,
      scripts=['bin/topser-pont'],
      zip_safe=False,
      test_suite='nose.collector',
      test_require=['nose'],)