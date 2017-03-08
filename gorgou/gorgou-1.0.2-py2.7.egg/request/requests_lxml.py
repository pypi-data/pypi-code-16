#!/usr/bin/env python
# -*-encoding:utf-8-*-

import re
import requests
from lxml import etree
cache_page = {}

'''
//div[@id=\"list\"]/ul/li
a/@href
div/text()
'''


def get_page_html(url, htmldec=None):
    r = requests.get(url)
    if r.status_code == 200:
        html = r.text
        if htmldec:
            html = html.decode(htmldec)
        return html


def get_page_html_by_xpath(url, xpath, htmldec=None):
    row = get_page_items_by_xpath(url, xpath, htmldec)[0]
    return etree.tostring(row, method='html', with_tail=False)


def get_page_htmls_by_xpath(url, xpath, htmldec=None):
    htmls = []
    rows = get_page_items_by_xpath(url, xpath, htmldec)
    for row in rows:
        html = etree.tostring(row, method='html', with_tail=False)
        htmls.append(html)
    return htmls

#
#


def get_cache_page_items_by_xpath(url, xpath, htmldec=None):
    if url in cache_page:
        page = cache_page[url]
        rows = page.xpath(xpath)
        return rows
    r = requests.get(url)
    if r.status_code == 200:
        html = r.text
        if htmldec:
            # html = html.decode('utf-8')
            html = html.decode(htmldec)
        page = etree.HTML(html)
        cache_page[url] = page
        rows = page.xpath(xpath)
        return rows

#
#


def get_page_items_by_xpath(url, xpath, htmldec=None):
    r = requests.get(url)
    if r.status_code == 200:
        html = r.text
        return get_html_items_by_xpath(html, xpath, htmldec)


def get_html_items_by_xpath(html, xpath, htmldec=None):
    if htmldec:
        # html = html.decode('utf-8')
        html = html.decode(htmldec)
    page = etree.HTML(html)
    rows = page.xpath(xpath)
    return rows

#
#


def get_page_items_by_re(url, rre, htmldec=None):
    r = requests.get(url)
    if r.status_code == 200:
        html = r.text
        return get_html_items_by_re(html, rre, htmldec)


def get_html_items_by_re(html, rre, htmldec=None):
    if htmldec:
        html = html.decode(htmldec)
    return re.findall(rre, html)

#
#


def download_items_by_json(json_file_path):
    _conf = json_ext.load_file_to_obj(json_file_path)
    li = download_items_from_conf(_conf)
    return json_ext.dump_to_str(li)


def download_items_from_conf(_conf, _url=None):
    li = []
    if _conf['dir']:
        url = _conf['url'].encode('utf-8')
    else:
        url = _url
    url = _conf['bef'].encode('utf-8') + url
    r = requests.get(url)
    if r.status_code == 200:
        html = r.text
        page = etree.HTML(html.decode('utf-8'))
        rows = page.xpath(_conf['row'])
        cols = _conf['col']
        for row in rows:
            tmp = {}
            for col in cols:
                if col['read'] == 'SUB':
                    __url = row.xpath(col['SUB']['url'])[0].encode('utf-8')
                    tmp[col['name']] = download_items_from_conf(col['SUB'], __url)
                if col['read'] == 'xpath':
                    tmp[col['name']] = row.xpath(col['path'])[0].encode('utf-8')
                    # if col['read'] == 'css':
                    #     ele = row.cssselect(col['path'])[0]
                    #     tmp[col['name']] = ele.get('class').encode('utf-8')
            li.append(tmp)
        return li
