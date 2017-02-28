import sys
import operator

# REDUCERS
dict_reducer = operator.getitem
instance_reducer = getattr

# MODULE
get_module = lambda x: sys.modules[x]
