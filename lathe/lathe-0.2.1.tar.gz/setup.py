from setuptools import setup

setup(
    name='lathe',
    version='0.2.1',
    description='Basic machine learning toolkit for BYU CS478',
    url='http://github.com/mwilliammyers/lathe',
    author='mwilliammyers',
    author_email='mwilliammyers@gmail.com',
    license='MIT',
    packages=['lathe'],
    install_requires=['liac-arff', 'numpy', 'scikit-learn', 'scipy'],
    keywords=['machine learning', 'ml', 'toolkit', 'byu', 'cs478'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
    zip_safe=False)
