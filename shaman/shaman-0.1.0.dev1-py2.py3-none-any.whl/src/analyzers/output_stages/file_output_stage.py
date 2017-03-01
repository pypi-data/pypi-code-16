import os
import json

from shaman.src.analyzers.abstract_stage import AbstractStage
from bson import json_util


class FileOutputStage(AbstractStage):
    def init_stage(self):
        self.message_fields_to_print = self.config['fields_to_print'].split(',')
        self.out_dir = self.config['out_dir']
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)
        self.file = None

    def do_stage(self, message):
        if not self.file:
            self.file = open(self.out_dir + '/' + self.consumer_name, 'a+')
        for field in self.message_fields_to_print:
            if message.__dict__[field]:
                if field in message.__dict__:
                    if not type(message.__dict__[field]) is dict:
                        if self.py_version == 2:
                            #raise NotImplementedError()
                            print('{} : {}'.format(field, message.__dict__[field]))
                        else:
                            #raise NotImplementedError()
                            print('{} : {}'.format(field, message.__dict__[field]))
                    else:
                        self.file.write('{}'.format(json.dumps(message.__dict__[field], default=json_util.default)))
                        self.file.write('\n')
        return message

    def shutdown(self):
        if self.file:
            self.file.close()
