from setuptools import setup, find_packages


def run_setup():

    setup(
        name='sklearn_dummies',
        version='0.2',
        author='Gustavo Sena Mafra',
        author_email='gsenamafra@gmail.com',
        description='Scikit-learn label binarizer with support for missing values',
        license='MIT',
        packages=find_packages(),
        url='https://github.com/gsmafra/sklearn-dummies',
        install_requires=['numpy', 'pandas', 'scikit-learn']
        )


if __name__ == '__main__':

    run_setup()
