#-*-coding:utf-8-*-
__author__ = 'cchen'


import pandas as pd
import warnings
import re


class DictList(dict):
    def append(self, key, value):
        self.value_type = list
        if key in self:
            self[key].append(value)
        else:
            self[key] = [value]

    def extend(self, key, values):
        self.value_type = list
        if key in self:
            self[key].extend(values)
        else:
            self[key] = values

    def values_to_set(self):
        self.value_type = set
        for k, v in self.iteritems():
            self[k] = set(v)


class DictSet(dict):
    def add(self, key, value):
        self.value_type = set
        if key in self:
            self[key].add(value)
        else:
            self[key] =  {value}


class DictInt(dict):
    def count(self, key, value=1):
        self.value_type = int
        if key in self:
            self[key] += value
        else:
            self[key] = value

    def to_csv(self, fp_out, columns=('k', 'v'), sort_values=True, sort_ascending=True, n_head=False):
        csv = pd.DataFrame(self.items(), columns=columns)
        if sort_values:
            csv.sort_values(columns[1], ascending=sort_ascending, inplace=True)
        if n_head:
            csv.head(n_head).to_csv(fp_out, index=False)
        else:
            csv.to_csv(fp_out, index=False)


class DictStr(dict):

    def concat(self, key, value, delimiter='\r'):
        self.value_type = str
        if key in self:
            self[key] += delimiter + value
        else:
            self[key] = value

    def wordcount(self, key):
        if key in self:
            return len(re.split(' |\r|\n', self[key]))
        else:
            raise KeyError("'%s' is not found" % (str(key)))


class Dict(DictList, DictSet, DictInt, DictStr):

    def len(self, key):
        if key in self:
            return len(self[key])
        else:
            raise KeyError("'%s' is not found" % (str(key)))

    def filter(self, function):
        for key, value in self.iteritems():
            if not function(value):
                self.pop(key, None)
