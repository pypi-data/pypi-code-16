# -*- coding: utf-8 -*-
from distutils.core import setup

LONGDOC = '''
CandyTable
==========

一個產生出CandyCrush初始table的小工具

Prerequisities


本套件pythno2跟python3皆通用<br>
若不能執行麻煩回報`Pull Requests`

## Installing

- 安裝 Install：`pip install CandyTable`

## Running & Testing

## Run

執行下列指令：

```
import CandyTable
c = CandyTable.CandyTable(10,10)
c.main()
```

- 輸入想要的顏色數量： ![table3](candy3.png)
- 最高支援到35色，若初始圖片不可能讓三顆糖果連線，則自動refresh： ![table35](candy35_refresh.png)

  ![table35-1](candy35final.png)

- 取得這張CandyTable的資訊：<br>
  `a.table`：

  ```
  {
    10: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    11: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    12: u'\x1b[0;32;40m \U0001f36c \x1b[0m',
    13: u'\x1b[0;31;40m \U0001f36c \x1b[0m',
    14: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    15: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    16: u'\x1b[0;32;40m \U0001f36c \x1b[0m',
    17: u'\x1b[0;31;40m \U0001f36c \x1b[0m',
    18: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    19: u'\x1b[0;32;40m \U0001f36c \x1b[0m',
    ...
    108: u'\x1b[0;33;40m \U0001f36c \x1b[0m',
    109: u'\x1b[0;33;40m \U0001f36c \x1b[0m'
  }
  ```

  x座標為1~10，y座標為0~9<br>
  字串一樣代表該位置的糖果是一樣的。

## Built With

- python2.7

## License

This package use `GPL3.0` License.

'''

# setup(
#     name = 'CandyTable',
#     packages = ['CandyTable'],
#     version = '1.4',
#     description = 'CandyTable compatible to python2 and python3',
#     # long_description = pypandoc.convert('README.md', 'rst')
#     long_description=LONGDOC,
#     author = 'davidtnfsh',
#     author_email = 'davidtnfsh@gmail.com',
#     url = 'https://github.com/david30907d/HomeWork/tree/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush',
#     download_url = 'https://github.com/david30907d/HomeWork/archive/v1.4.tar.gz',
#     keywords = ['CandyTable',],
#     classifiers = [],
#     license='GPL3.0',
#     install_requires=[
#     ],
#     zip_safe=True
# )

from distutils.core import setup
LONGDOC = """
jieba
=====
“结巴”中文分词：做最好的 Python 中文分词组件
"Jieba" (Chinese for "to stutter") Chinese text segmentation: built to
be the best Python Chinese word segmentation module.
完整文档见 ``README.md``
GitHub: https://github.com/fxsjy/jieba
特点
====
-  支持三种分词模式：
   -  精确模式，试图将句子最精确地切开，适合文本分析；
   -  全模式，把句子中所有的可以成词的词语都扫描出来,
      速度非常快，但是不能解决歧义；
   -  搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。
-  支持繁体分词
-  支持自定义词典
-  MIT 授权协议
在线演示： http://jiebademo.ap01.aws.af.cm/
安装说明
========
代码对 Python 2/3 均兼容
-  全自动安装： ``easy_install jieba`` 或者 ``pip install jieba`` / ``pip3 install jieba``
-  半自动安装：先下载 https://pypi.python.org/pypi/jieba/ ，解压后运行
   python setup.py install
-  手动安装：将 jieba 目录放置于当前目录或者 site-packages 目录
-  通过 ``import jieba`` 来引用
"""

setup(name='CandyTable',
      version='1.5',
      description='Chinese Words Segementation Utilities',
      long_description=LONGDOC,
      author='Sun, Junyi',
      author_email='davidtnfsh@gmail.com',
      url='https://github.com/fxsjy/CandyTable',
      license="MIT",
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='NLP,tokenizing,Chinese word segementation',
      packages=['CandyTable'],
)
