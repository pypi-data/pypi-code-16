# -*- coding: utf-8 -*-
import base64
import urllib2
import json
import uuid


def generate_code():
    json_file = open("example.json", "w")
    # doc_json=json_file.readline()
    #doc_json=get_doc('ORDER','3d2e4546485058b73a0eade67e251d47926745b5')
    doc_json=get_last_doc()
    # json_file.write(doc_json)
    # file.close()
    list_doc=json.loads(doc_json)['result']
    for result in list_doc:
        interfaceName = result['className']
        module_name = str(interfaceName).split(".")[1].capitalize()
        apis_file = open("../sdk/apis/" + module_name.lower() + "_service.py", "w")
        apis_file.write("# -*- coding: utf-8 -*-\n\n\n")
        apis_file.write("class " + module_name + "Service:\n\n")
        apis_file.write("    __client = None\n\n")
        apis_file.write("    def __init__(self, client):\n        self.__client = client\n\n")
        methods = result['classMethods']
        for method in methods:
            action = method['methodName']
            methodParams = method['methodParams']
            join_params = ''
            join_params_json = '{'
            for param in methodParams:
                field_name = str(param["fieldName"])
                join_params = join_params + ", " + camel_to_underline(field_name)
                if (param == methodParams[-1]):
                    join_params_json = join_params_json + '"' + field_name + '": ' + camel_to_underline(field_name)
                else:
                    join_params_json = join_params_json + '"' + field_name + '": ' + camel_to_underline(
                        field_name) + ", "
            join_params_json = join_params_json + "}"
            apis_file.write("    def " + camel_to_underline(str(action).split(".")[2]) + "(self" + join_params + "):\n")
            apis_file.write('        return self.__client.call("' + action + '", ' + join_params_json + ')\n\n')
        apis_file.close()


def camel_to_underline(camel_format):
    underline_format=''
    if isinstance(camel_format, str):
        for _s_ in camel_format:
            underline_format += _s_ if _s_.islower() else '_'+_s_.lower()
    return underline_format


def get_doc(type, version):
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    remote_url='https://open-api.shop.ele.me/operating/invoke?method=ShuttleService.getESDoc'
    request_json={
        "id":  str(uuid.uuid4()),
        "method": "getESDoc",
        "service": "ShuttleService",
        "params": {"serviceType": type, "docVersion": version},
        "metas": {"appName": "melody", "appVersion": "4.4.0"},
        "ncp": "2.0.0"
    }
    request = urllib2.Request(remote_url, json.dumps(request_json).encode('utf-8'), headers)
    response = urllib2.urlopen(request)
    result = response.read()
    return result.decode('utf-8')


def get_last_doc():
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    remote_url='https://open-api.shop.ele.me/operating/invoke?method=ShuttleService.getESDoc'
    request_json={
        "id":  str(uuid.uuid4()),
        "method": "getLatestESDoc",
        "service": "ShuttleService",
        "params": {},
        "metas": {"appName":"melody","appVersion":"4.4.0"},
        "ncp":"2.0.0"
    }
    request = urllib2.Request(remote_url, json.dumps(request_json).encode('utf-8'), headers)
    response = urllib2.urlopen(request)
    result = response.read()
    return result.decode('utf-8')

if __name__ == '__main__':
    generate_code()