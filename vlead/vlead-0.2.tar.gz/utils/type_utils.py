
import re
import types
import datetime
import json
from sqlalchemy.orm.collections import InstrumentedList
from flask import make_response

def is_inst(cls):
    def fn(a):
        return a.__class__.__name__ == cls.__name__
    return fn

is_int = is_inst(int)
is_bool = is_inst(bool)
is_str = is_inst(str)
is_dict = is_inst(dict)
is_normal_list = is_inst(list)
is_instrumented_list = is_inst(InstrumentedList)
is_list = lambda ls: is_normal_list(ls) or is_instrumented_list(ls)
is_string = is_inst(str)
is_unicode = is_inst(unicode)
is_str_or_none = lambda str: is_str(str) or str == None

def is_alphabetic_str(value):
    if (isinstance(value, str) and not re.search('[^a-zA-Z. ]+', value)):
        return True
    else:
        return False


def is_email_str(value):
    if isinstance(value, str) and re.search('[^@]+@[^@]+\.[^@]+', value):
        return True
    else:
        return False

def is_url(url):
    if re.search('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url):
        return True
    else:
        return False

def is_date(value):
    return isinstance(value, datetime.date)

def is_none(value):
    return value == None

# return a list of dicts as json with correct mime types
# flask does not provide a jsonify for lists; hence this method
def jsonify_list(data):
    if type(data) is not list:
        raise Exception('jsonify_list function accepts only a list')

    return make_response(json.dumps(data), 200,
                         {'content-type': 'application/json'})


def check_pred(p):
    def fn(a):
        if p(a):
            return a
        else:
            raise TypeError('arg %s does not satisfy type predicate %s' % (a, p))
    return fn

check_alphabetic_str = check_pred(is_alphabetic_str)
check_email_str = check_pred(is_email_str)
check_string = check_pred(is_string)
check_date = check_pred(is_date)
check_int = check_pred(is_int)

def check_inst(cls):
    return check_pred(is_inst(cls))

check_function =  check_inst(types.FunctionType)
check_dict = check_inst(dict)
check_list = check_inst(list)
check_str = check_inst(str)
check_int = check_inst(int)
check_pos_int = check_pred(lambda arg: check_int(arg) and arg > 0)
check_non_neg_int = check_pred(lambda arg: check_int(arg) and arg >= 0)

def check_inv(inv, *name):
    # args is a dictionary
    def fn(args):
        if inv(args):
            args
        else:
            if name == []:
                raise TypeError("invariant fails on args %s" % args)
            else:
                raise TypeError("invariant for class %s fails on args %s" % (name[0], args))
    return fn
