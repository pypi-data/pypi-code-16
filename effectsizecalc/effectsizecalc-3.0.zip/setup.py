from setuptools import setup

setup(name='effectsizecalc',
      version='3.0',
      description='Tool for calculating effect size between group means',
      url='https://github.com/sudiptatung/EffectSizeCalculator.git',
      author='Sudipta Tung',
      author_email='sudiptatung@gmail.com',
      license='MIT',
      packages=['effectsizecalc'],
      install_requires=[
          'openpyxl',
      ],
      zip_safe=False)
