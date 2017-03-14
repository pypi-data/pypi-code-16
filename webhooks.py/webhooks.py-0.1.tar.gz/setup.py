from setuptools import setup


setup(
    name="webhooks.py",
    version="0.1",
    license="MIT",
    author='Mario César Señoranis Ayala',
    author_email='mariocesar.c50@gmail.com',
    packages=["webhooks"],
    package_dir={'webhooks': 'webhooks'},
    url='https://github.com/mariocesar/webhoooks.py',
    zip_safe=True,
    entry_points={
        'console_scripts': ['webhooks.py=webhooks:main'],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)