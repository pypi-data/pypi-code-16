from setuptools import setup

setup(name='neurodesign',
      version='0.0.23',
      description='Package for design optimisation for fMRI experiments',
      author='Joke Durnez',
      author_email='joke.durnez@gmail.com',
      license='MIT',
      packages=['neurodesign'],
      package_dir={'neurodesign':'src'},
      package_data={'neurodesign':['media/NeuroDes.png']},
      zip_safe=False)
