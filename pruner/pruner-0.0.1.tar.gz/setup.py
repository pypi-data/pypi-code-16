from distutils.core import setup

setup(author='Matthew Egan',
      author_email='matthewj.egan@hotmai.com',
      description='A CLI tool for pruning your overgrown requirements file',
      name='pruner',
      py_modules=[
          'pruner.pruner',
      ],
      entry_points={
            'console_scripts': [
                  'pruner = pruner.pruner:main'
            ]
      },
      version='0.0.1'
)
