"""For distribution.
"""

from setuptools import setup, find_packages

# build with sdist to make sure platform compatibility.
setup(
    name="deepmodels",
    version="0.1.7",
    description="framework for build, train and test deep learning models",
    url="https://github.com/flyfj/deepmodels",
    author="Jie Feng",
    author_email="jiefengdev@gmail.com",
    license="MIT",
    include_package_data=True,
    packages=find_packages(exclude=["docs"]),
    install_requires=["numpy==1.11.2", "scipy==0.18.1", "scikit_image==0.12.3", "tensorflow==0.12.1", "tqdm==4.10.0", "Pillow==4.0.0", "cv2==1.0", "lasagne==0.1", "scikit_learn==0.18.1"])
