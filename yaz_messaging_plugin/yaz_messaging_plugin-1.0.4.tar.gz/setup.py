from setuptools import setup

setup(name="yaz_messaging_plugin",
      packages=["yaz_messaging_plugin"],
      version="1.0.4",
      description="A symfony message translation plugin for YAZ",
      author="Boudewijn Schoon",
      author_email="boudewijn@zicht.nl",
      url="http://github.com/boudewijn-zicht/yaz_messaging_plugin",
      license="MIT",
      zip_safe=False,
      install_requires=["yaz", "pyyaml"],
      scripts=["bin/yaz-messaging"],
      test_suite="nose.collector",
      tests_require=["nose"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3.5",
          "Programming Language :: Python :: 3.6"
      ])
