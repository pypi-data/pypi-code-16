# -*- encoding: utf-8 -*-

import re
import time
import json
import random
import base64
import shutil
import requests
from os import path
from Crypto.Hash import SHA, MD5
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

def set_kwargs_default(key, value, kwargs):
    if not kwargs.get(key):
            kwargs[key] = value
    # print kwargs

def get_default_email_title(user):
    title = user.__dict__.get('emailtitle')
    time_str = str(time.strftime("%Y%m%d%H%M%S", time.localtime()))
    if title:
        title += ' - ' + time_str
    else:
        title = time_str
    return title

def get_random_sign_position():
    x = "0." + str(random.randint(1, 80))
    y = "0." + str(random.randint(1, 80))
    return (x, y)

def get_sign_data(*args):
    non_empty = [_f for _f in args if _f]
    if non_empty is None or len(non_empty) == 0:
        return ''
    else:
        return '\n'.join([str(i) for i in non_empty])

def md5_encode(string):
    if not type(string) is bytes:
        string = string.encode('utf-8')
    h = MD5.new()
    h.update(string)
    return h.hexdigest()

def get_rsa_sign(sign_data, key):
    sign_data = sign_data.encode('utf-8')
    # sign_data = str(sign_data, encoding='utf-8')
    sha1 = SHA.new()
    sha1.update(sign_data)
    key_der = base64.b64decode(key)
    rsa_key = RSA.importKey(key_der)
    rsa = PKCS1_v1_5.new(rsa_key)
    return base64.b64encode(rsa.sign(sha1))

def file_to_stream(file_path, base64_encode=True):
    if path.isfile(file_path):
        with open(file_path, 'rb') as fp:
            stream = fp.read()
        if base64_encode:
            return base64.b64encode(stream)
        else:
            return stream
    else:
        raise AssertionError('[{0}] is not a regular file'.format(file_path))

def get_file_ext(file_path):
    file_name = path.basename(file_path)
    file_ext = path.splitext(file_name)[1]
    return file_ext[1:]

def get_file_name(file_path):
    return path.basename(file_path)

def load_json_from_file(filepath):
    '''Read JSON string from file, and convert it into a JSON dict.
    
    :param str filepath: full path of the JSON file.
    
    :returns: JSON dict.
    '''
    with open(filepath, 'r')  as f:
        data = json.load(f)
    
    return data

def load_json_from_string(json_str):
    '''Convert a JSON string into JSON dict.
    
    :param str: JSON format string.
    
    :returns: JSON dict.
    '''
    return json.loads(json_str)

def json_to_string(json_dict):
    '''Convert JSON dict to JSON string.
    '''
    return json.dumps(json_dict)

def get_x_value_by_y(jdata, x, y, y_value):
    x_path = '$..%s' % x
    y_path = '$..%s' % y
    
    x_match = [m for m in parse(x_path).find(jdata)]
    # cannot find x in json data
    if not x_match:
        raise AssertionError("Cannot find any [%s] in JSON data" % x)
    
    y_match = [m for m in parse(y_path).find(jdata)]
    # cannot find y in json data
    if not y_match:
        raise AssertionError("Cannot find any [%s] in JSON data" % y)
    
    y_parent_path = []
    for i in y_match:
        if i.value == y_value:
            y_p_path = re.sub(r'\.%s' % y, '', str(i.full_path))
            y_parent_path.append(y_p_path)
    
    # cannot find y with y_value
    if not y_parent_path:
        raise AssertionError("Cannot find any [%s] with value [%s]" % (y, y_value))
    
    x_values = []
    for i in x_match:
        x_p_path = re.sub(r'\.%s' % x, '', str(i.full_path))
        if x_p_path in y_parent_path:
            x_values.append(i.value)
    
    if len(x_values) == 1:
        return x_values[0]
    else:
        return x_values

def download_https_file(url, file_path):
    if not path.isabs(file_path):
        var = BuiltIn().get_variables()
        log_dir = var['${OUTPUTDIR}']
        file_path = path.join(log_dir, file_path)
    
    requests.packages.urllib3.disable_warnings()
    r = requests.get(url, verify=False, stream=True)
    r.raw.decode_content = True
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
    
    return file_path

def parse_verification_code(msg):
    match = re.search(r'\d\d\d\d\d\d', msg, re.I)
    if match:
        return match.group(0)
    else:
        return ""

def shorten_long_dict(d, max_len=1000):
    r = {}
    for k,v in d.items():
        if len(v) > max_len:
            r[k] = str(v[:15]) + str(' ...... ') + str(v[-15:])
        else:
            r[k] = v
    
    return r

