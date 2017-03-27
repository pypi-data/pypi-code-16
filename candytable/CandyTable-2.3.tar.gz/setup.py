# -*- coding: utf-8 -*-
from distutils.core import setup
long_description = '''
CandyTable
==========

一個產生出CandyCrush初始table的小工具

Getting Started
---------------

These instructions will get you a copy of the project up and running on
your local machine for development and testing purposes. See deployment
for notes on how to deploy the project on a live system.

Prerequisities
~~~~~~~~~~~~~~

| 本套件pythno2跟python3皆通用
| 若不能執行麻煩回報\ ``Pull Requests``

Installing
~~~~~~~~~~

-  安裝 Install：\ ``pip install CandyTable``

Running & Testing
-----------------

Run
---

執行下列指令：

::

    import CandyTable
    c = CandyTable.CandyTable(10,10)
    c.main()

-  輸入想要的顏色數量：

.. figure:: https://github.com/david30907d/HomeWork/blob/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush/candy3.png?raw=true
   :alt: table3

   table3

-  最高支援到35色，若初始圖片不可能讓三顆糖果連線，則自動refresh：

.. figure:: https://github.com/david30907d/HomeWork/blob/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush/candy35_refresh.png?raw=true
   :alt: table35

   table35

.. figure:: https://github.com/david30907d/HomeWork/blob/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush/candy35final.png?raw=true
   :alt: table35-1

   table35-1

-  ``a.table``\ ：可以取得這張CandyTable的資訊

``{     10: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     11: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     12: u'\x1b[0;32;40m \U0001f36c \x1b[0m',     13: u'\x1b[0;31;40m \U0001f36c \x1b[0m',     14: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     15: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     16: u'\x1b[0;32;40m \U0001f36c \x1b[0m',     17: u'\x1b[0;31;40m \U0001f36c \x1b[0m',     18: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     19: u'\x1b[0;32;40m \U0001f36c \x1b[0m',     ...     108: u'\x1b[0;33;40m \U0001f36c \x1b[0m',     109: u'\x1b[0;33;40m \U0001f36c \x1b[0m' }``

| 座標系統從左上角開始數
| 左上角為10 右下角為109 y座標為1到10，x座標為0到9
| 字串一樣代表該位置的糖果是一樣的。

Break down into end to end tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

not yet.

And coding style tests
~~~~~~~~~~~~~~~~~~~~~~

目前沒有coding style tests...

Deployment
----------

CandyTable 只是一個小玩具而已，\ ``pip install CandyTable`` 就好

Built With
----------

-  python2.7

Contributors
------------

-  **張泰瑋** `david <https://github.com/david30907d>`__

License
-------

This package use ``GPL3.0`` License.

Acknowledgments
---------------

'''

setup(
    name = 'CandyTable',
    packages = ['CandyTable'],
    version = '2.3',
    long_description=long_description,
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/david30907d/HomeWork/tree/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush',
    download_url = 'https://github.com/david30907d/HomeWork/archive/v2.3.tar.gz',
    keywords = ['CandyTable',],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
    ],
    zip_safe=True
)
