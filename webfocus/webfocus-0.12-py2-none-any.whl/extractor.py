#!/usr/bin/env python
#-*-coding:utf-8-*- 
from lxml.html import fromstring,tostring
import requests
import re
import pyquery
from HTMLParser import HTMLParser
"""
from lxml import etree#导入lxml库  
parser=etree.XMLParser(load_dtd= True)#首先根据dtd得到一个parser(注意dtd文件要放在和xml文件相同的目录)  
tree = etree.parse("dblp.xml",parser)#用上面得到的parser将xml解析为树结构  
root = tree.getroot()#获得该树的树根  
for article in root:#这样便可以遍历根元素的所有子元素(这里是article元素)  
    print "元素名称：",article.tag#用.tag得到该子元素的名称  
    for field in article:#遍历article元素的所有子元素(这里是指article的author，title，volume，year等)  
        print field.tag,":",field.text#同样地，用.tag可以得到元素的名称，而.text可以得到元素的内容  
    mdate=article.get("mdate")#用.get("属性名")可以得到article元素相应属性的值  
    key=article.get("key")  
    print "mdate:",mdate  
    print "key",key  
    print ""#隔行分开不同的article元素
##
#   http://blog.csdn.net/xia7139/article/details/10195849
##
判断要素：
*   标签语义
*   标签密度
*   标签兄弟节点相似性,应该是指：其它三个向量都相同，但是这样违背朴素贝叶斯
*   标签外链
首先处理
p 标签，密度大于6，兄弟节点相似3，外链接0
a 标签，密度0，兄弟相似性1，外链接1
a 标签，密度1，兄弟节点相似性1，外链接1
"""
__version__ = "0.12"

class ChoiceTree(object):
    """
        生成的选择树
    """

    def __init__(self):
        """
            生成选择树
        """
        self.choice_tree = []

        for i in range(0,5):
            for j in range(0,pow(2,i)):
                if j % 2 == 0:
                    self.choice_tree.append(1)
                else:
                    self.choice_tree.append(0)

        answer_left = (True,False,True,False,False,False,False,False)
        answer_right = (True,False,True,False,False,False,False,False)
        for m in answer_left:
            self.choice_tree.append(m)
            self.choice_tree.append(m) 

        for n in answer_right:
            self.choice_tree.append(n)
            self.choice_tree.append(n)

    def get_choice_tree_size(self):
        """
            主要查看生成树是否正确
        """
        return len(self.choice_tree)       

    def show_choice_tree(self):
        """
            显示选择树
        """
        index = 1
        step = 0
        for i in self.choice_tree:
            print i," ",

            if(index == pow(2,step)):
                step += 1
                index = 1
                print "\n"
            else:            
                index += 1

    def info_or_noise(self,*code):
        """
            评判一个节点是否信息还是噪声
        """
        last_postion = 0
        for c in code:
            if c == 1:
                last_postion = last_postion * 2 + 1
            else:
                last_postion = last_postion * 2 + 2
        
        return self.choice_tree[last_postion*2+1]
        

def extract_from_url(source,text_only):
    """
        html文本当中提取正文
    """
    if re.match(r"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?",source):
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
        response = requests.get(source,headers=headers)
        html_source = pyquery.PyQuery(response.text.encode(response.encoding).decode(response.apparent_encoding,"ignore"))
        #html_source = pyquery.PyQuery(response.content)
        return extract_from_htmlstring(html_source,text_only)
    else:
        return ["NotAnValideUrl","NotAnValideUrl"]
        
def extract_from_htmlstring(source,text_only):
    """
        给定url 提取文章
        html_source = None 
        if re.match(r"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?",source):
            response = requests.get(source)
            html_source = pyquery.PyQuery(response.text.encode(response.encoding).decode(response.apparent_encoding,"ignore"))
        else:
    """
    html_source = pyquery.PyQuery(source)

    html_source("style").remove()
    html_source("script").remove()
    html_dom = fromstring(html_source.html())
    ##
    # 计算所有p标签的向量
    ##
    choice_tree = ChoiceTree()

    node_label_list = html_dom.xpath("//p | //a")

    for p in node_label_list:
        tag = p.tag
        p_parent = p.getparent()
        similaritys = len(p_parent.xpath("./%s" % tag))
        similarity = 1 if similaritys > 2 else 0 # similarity
        text = p.text_content()
        text = text if text else " "

        density = 1 if len(text) > 8 else 0     # density

        label = 1                               # label
        not_outlink = 1 if tag != 'a' else 0    # notoutlink
        
        yes_or_no = choice_tree.info_or_noise(*[label,density,similarity,not_outlink])

        if yes_or_no:
            #print "set %s to True" % p
            p.usefull = True
            p.similarity = similaritys
            p.density = len(text)
        else:
            p.usefull = False
            p.similarity = similaritys
            p.density = len(text)            
            #print " %s is not a valide content part" % p

    ##
    # 下面来计算信噪比
    ##
    possible_main_body = html_dom.xpath("//div")
    if not possible_main_body:
        return [None,None]
    max_ratio = 0
    the_info_node = possible_main_body[0]
    the_noise_node = possible_main_body[0]
    noise_ratio = 65535

    for div in possible_main_body:
        [p,n] = calculate_non_leaf_node_info(div)
        ratio = 0.0
        if n <= 0:
            ratio = float(p) / (n + 1)
        else:
            ratio = float(p) / n

        if(ratio > max_ratio):
            max_ratio = ratio
            the_info_node = div

        if(ratio < noise_ratio):
            noise_ratio = ratio 
            the_noise_node = div 
    if not text_only:
        content = re.sub(r"\s{2,}"," ",tostring(the_info_node))
        noise = re.sub(r"\s{2,}"," ",tostring(the_noise_node))
        parser = HTMLParser()
        return [parser.unescape(content),parser.unescape(noise)]
    else:
        content = re.sub(r"\s{2,}"," ",the_info_node.text_content())
        noise = re.sub(r"\s{2,}"," ",the_noise_node.text_content())
        return[content,noise]
    

def calculate_non_leaf_node_info(node):
    """
        计算每个非叶子节点的信息含量
    """
    if not node.getchildren():
        if hasattr(node,"usefull"):
            if getattr(node,"usefull"):
                info = getattr(node,"similarity")+getattr(node,"density")/8
                return [info,0]
            else:
                info = getattr(node,"similarity")/8+getattr(node,"density")/16
                return [0,info]
        else:
            return [0,1]

    positive_sum = 0
    negtive_sum = 0
    child_nodes = node.getchildren()
    for child_node in child_nodes:
        p = 0
        n = 0
        # 这里节省开销，如果算过了信号和噪声总量，那么缓存起来，下一轮就不再计算了
        if child_node.tag=='div':
            if hasattr(child_node,"IE") and hasattr(child_node,"NE"):
                p = getattr(child_node,"IE")
                n = getattr(child_node,"NE")
            else:
                p,n= calculate_non_leaf_node_info(child_node)
                setattr(child_node,"IE",p)
                setattr(child_node,'NE',n)
        else:
            p,n= calculate_non_leaf_node_info(child_node)

        positive_sum += p
        negtive_sum += n
    return [positive_sum,negtive_sum]
    
def auto_decode_to_unicode(response):
    """
        自动解码
        Content-Type:text/html; charset=GB2312
    """
    encoding_in_content_type = response.headers.get("Content-Type")
    encoding_in_header = re.search(r"charset=(?P<encoding>.+)",encoding_in_content_type)
    if encoding_in_header:
        # response header 当中有encoding
        return encoding_in_header.group("encoding")
    else:
        
        pass

if __name__ == "__main__":
    #choice_tree = ChoiceTree()
    #choice_tree.show_choice_tree()
    # Content-Type:text/html; charset=GB2312
    url = "http://finance.ifeng.com/a/20170228/15218154_0.shtml"
    info,noise  = extract_from_url(url)
    print info
    print "--------------------------------------------"
    print noise
            
        