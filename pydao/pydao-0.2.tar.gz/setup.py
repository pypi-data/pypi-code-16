from setuptools import setup, find_packages

def get_requirements():
    with open('requirements.txt', 'r') as f:
        return f.readlines()

setup(name='pydao',
    version='0.2',
    description='simple mysql access api based on sqlalchemy and pymysql',
    url='https://github.com/yimian/pydao',
    author='zhangjinjie',
    author_email='zhangjinjie@yimian.com.cn',
    packages=find_packages(),
    install_requires=get_requirements(),
    zip_safe=False)
