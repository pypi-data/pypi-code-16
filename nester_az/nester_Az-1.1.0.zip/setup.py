from distutils.core import setup #python发布工具导入setup函数
setup(
    name='nester_Az',
    version='1.1.0',
    py_modules=['nester'],
    author='hfpython',
    author_email='hfpython@headfirstlabs.com',
    url='http://www.headfirstlabs.com',
    description='test and study',
    )
#构建发布：python setup.py sdist
#发布安装副本：python setup.py install
#pypi注册：python setup.py register
#pypi发布：python setup.py sdist upload
