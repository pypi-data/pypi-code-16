try:
   input = raw_input
except NameError:
    input = input

try:
   basestring = basestring
except NameError:
    basestring = str
