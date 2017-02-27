#coding=utf8

import urllib


class Paginator(object):
    total = 0 
    num_per_page = 30
    current = 0 
    offset = 3 
    paras = {}
    p_argname = 'page'

    _prevlist = None
    _nextlist = None
    _page_total = None
    def __init__(self, current, total=None, num_per_page=None, p_argname=None,
                 paras=None, offset=None):
        """ 
        :param current: current page number, start from 1
        :param p_argname: pagination parameter name
        :param paras: other parameters, dictionary
        :param offset: show how many page numbers before and after current page
        """
        if total:
            self.total = total
        if num_per_page:
            self.num_per_page = num_per_page
        if current:
            self.current= current
        if p_argname:
            self.p_argname = p_argname
        if offset:
            self.offset = offset
        if paras: 
            self.paras = paras
            for k, v in self.paras.items():
                assert isinstance(k, str)
                if not v:
                    self.paras[k] = ''
                if isinstance(v, unicode):
                    self.paras[k] = v.encode('utf8')

        if self.current > 1:
            self.show_prevbutton = True
        else:
            self.show_prevbutton = False

        if self.current < (self.pages):
            self.show_nextbutton = True
        else:
            self.show_nextbutton = False

        if self.prevlist and self.prevlist[0] != 1:
            self.show_firstpage = True
        else:
            self.show_firstpage = False

        if self.nextlist and self.nextlist[-1] < (self.pages):
            self.show_lastpage = True
        else:
            self.show_lastpage = False
            
    @property
    def pages(self):
        "total page number."
        if self._page_total != None:
            return self._page_total
        self._page_total = (self.total / self.num_per_page)
        if self.total % self.num_per_page != 0:
            self._page_total += 1
        return self._page_total

    @property
    def prevlist(self):
        "start number is 1"
        if self._prevlist != None:
            return self._prevlist

        self._prevlist = []
        _prev = self.current 
        while len(self._prevlist) < self.offset:
            _prev -= 1
            if _prev < 1:
                break
            self._prevlist.insert(0, _prev)
        return self._prevlist

    @property
    def nextlist(self):
        "start number is 1"
        if self._nextlist != None:
            return self._nextlist

        self._nextlist = []
        _next = self.current
        while len(self._nextlist) < self.offset:
            _next += 1
            if _next > self.pages:
                break
            self._nextlist.append(_next)
        return self._nextlist
            
    def param(self, page, **kwarg):
        """
        encode url parameters with given `page` number.
        """
        kwarg.update(self.paras)
        kwarg[self.p_argname] = page
        paras = urllib.urlencode(kwarg)
        return paras

