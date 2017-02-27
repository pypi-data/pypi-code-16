# coding=utf8

from lxml import etree


def para_clean(html, img_handle=None, pre_handle=None, header_handle=None):
    """
    clean html doc
    :param {tag}_handle: pass element into img_handle
    :rtype: unicode string
    """
    element = etree.fromstring(html, etree.HTMLParser(encoding='utf8'))

    def recur(element):
        # comment
        if not isinstance(element.tag, (str, unicode)):
            element.getparent().remove(element)
            return

        # javascript / css
        if element.tag.lower() in ('javascript', 'style'):
            element.getparent().remove(element)
            return

        if element.tag.lower() == 'img' and img_handle:
            img_handle(element)
        if element.tag.lower() == 'pre' and pre_handle:
            pre_handle(element)
        if element.tag.lower() in ('h1', 'h2', 'h3', 'h4', 'h5') and header_handle:
            pre_handle(element)

        if element.tag.lower() in ('noscript',):
            element.tag = 'p'

        keys = element.attrib.keys()
        for key in keys:
            if key in ('href', 'title', 'alt', 'src'):
                continue
            element.attrib.pop(key)

        for child in element:
            recur(child)

    for ele in element:
        recur(ele)

    result = []
    for ele in element[0]: # html>body>elements
        html = etree.tostring(ele, encoding='utf8', method='html')
        html = html.encode('utf8') if isinstance(html, unicode) else html
        result.append(html)
    return (''.join(result)).decode('utf8')
