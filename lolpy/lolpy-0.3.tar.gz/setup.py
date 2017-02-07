from setuptools import setup

setup(name='lolpy',
      version='0.3',
      description='Package for Interaction with the League of Legends API',
      url='https://github.com/abousquet/lolpy',
      author='Adam Bousquet',
      author_email='ajbousquet6@gmail.com',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Natural Language :: English",
          "Programming Language :: Python :: 3.6",
          "Topic :: Games/Entertainment :: Real Time Strategy"
      ],
      license='MIT',
      packages=['lolpy'],
      zip_safe=False,
      install_requires=["lolpy>=0.1",
                        "numpy==1.12.0",
                        "requests==2.12.4"])
