#-*-coding:utf-8-*-
__author__ = 'cchen'


import csv
class A(csv.excel):
    delimiter = '@'


with open('__init__.py', 'r') as i:
    csv.register_dialect('a', A)
    csvreader = csv.reader(i, dialect='a',ddd=1)
b = A()
print globals()
print 1


import textprep
a = textprep.preprocessor('twitter', is_remove_repeated_char=False).process()
