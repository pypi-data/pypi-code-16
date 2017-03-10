from setuptools import setup


setup(
    name='cntalib',
    version='20170310',
    description='China stock market technical analysis library',
    keywords='China stock market technical analysis library',
    url='https://github.com',
    author='Jian Xue',
    author_email='cntalib@qq.com',
    license='GNU',
    packages=[
        'cntalib',
        'cntalib.Reference',
        'cntalib.Logic',
	'cntalib.K_matching',
    ],
    install_requires=[
        'numpy',
        'pandas',
    ],
    zip_safe=False
)
