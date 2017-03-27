# -*- coding: utf-8 -*-
from distutils.core import setup

LONGDOC = '''
<h1><a id="CandyTable_0"></a>CandyTable</h1>
<p>一個產生出CandyCrush初始table的小工具</p>
<h2><a id="Prerequisities_4"></a>Prerequisities</h2>
<p>本套件pythno2跟python3皆通用&lt;br&gt;<br>
若不能執行麻煩回報<code>Pull Requests</code></p>
<h2><a id="Installing_9"></a>Installing</h2>
<ul>
<li>安裝 Install：<code>pip install CandyTable</code></li>
</ul>
<h2><a id="Running__Testing_13"></a>Running &amp; Testing</h2>
<h2><a id="Run_15"></a>Run</h2>
<p>執行下列指令：</p>
<pre><code>import CandyTable
c = CandyTable.CandyTable(10,10)
c.main()
</code></pre>
<ul>
<li>
<p>輸入想要的顏色數量： <img src="candy3.png" alt="table3"></p>
</li>
<li>
<p>最高支援到35色，若初始圖片不可能讓三顆糖果連線，則自動refresh： <img src="candy35_refresh.png" alt="table35"></p>
<p><img src="candy35final.png" alt="table35-1"></p>
</li>
<li>
<p>取得這張CandyTable的資訊：&lt;br&gt;<br>
<code>a.table</code>：</p>
<pre><code>{
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
</code></pre>
<p>x座標為1<sub>10，y座標為0</sub>9&lt;br&gt;<br>
字串一樣代表該位置的糖果是一樣的。</p>
</li>
</ul>
<h2><a id="Built_With_54"></a>Built With</h2>
<ul>
<li>python2.7</li>
</ul>
<h2><a id="License_58"></a>License</h2>
<p>This package use <code>GPL3.0</code> License.</p>

'''

setup(
    name = 'CandyTable',
    packages = ['CandyTable'],
    version = '1.6',
    description = 'CandyTable compatible to python2 and python3',
    long_description=LONGDOC,
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/david30907d/HomeWork/tree/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush',
    download_url = 'https://github.com/david30907d/HomeWork/archive/v1.6.tar.gz',
    keywords = ['CandyTable',],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
    ],
    zip_safe=True
)
