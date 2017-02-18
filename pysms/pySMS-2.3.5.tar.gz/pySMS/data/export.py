import json
import gzip
import os


class Export:

    def __init__(self):
        self.data_files_list = self.get_data_files_list()

    @staticmethod
    def get_data_files_list():
        data = {}
        files = [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__)))]
        for file in files:
            data[file] = file
        return data

    @staticmethod
    def unzip_from_gzip(file):
        with gzip.open(os.path.dirname(os.path.realpath(__file__)) + '\\' + file, 'rb') as f:
            file_content = f.read()
        return {'file': file, 'content': file_content, 'type': type(file_content)}

    @staticmethod
    def zip_to_gzip(file, data_obj):
        _f = file.split('.')
        with gzip.open(os.path.dirname(os.path.realpath(__file__)) + '\\' + file + ".gz", 'wb')as f:
            f.write(data_obj)
        f.close()

    @staticmethod
    def import_json_file(file):
        with open(file)as data_file:
            content = json.load(data_file)
        return {'file': file, 'content': content, 'type': type(content)}

    @staticmethod
    def convert_to_dict(obj):
        return json.loads(obj)

    @staticmethod
    def convert_to_gzip_obj(obj):
        gzip_obj = json.dumps(obj)
        return {'origin_type': type(obj), 'new_type': type(gzip_obj), 'obj': gzip_obj}
