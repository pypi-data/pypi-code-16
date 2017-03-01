from setuptools import setup, find_packages

setup(
    name = 'juspay',
    version = '1.1.2',
    description = 'Python client for JusPay Express Checkout API',
    url = 'https://www.juspay.in ',
    author = 'JusPay',
    author_email = 'ninjas@juspay.in',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages = find_packages(),
    keywords='juspay expresscheckout payments',
    install_requires = ['requests'],
)
