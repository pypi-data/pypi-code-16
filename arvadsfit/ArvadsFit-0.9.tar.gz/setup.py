from setuptools import setup

setup(name='ArvadsFit',
      version='0.9',
      description='A custom wrapper of IMinuit',
      url='https://github.com/Arvad/ArvadsFit',
      author='Asbjorn Arvad Jorgensen',
      author_email='Arvad91@gmail.com',
      license='MIT',
      packages=['ArvadsFit'],
      install_requires=[
                        'numpy >= 1.11',
                        'iminuit >= 1.2',
                        'probfit >= 1.0',
                         ],
      zip_safe=False)