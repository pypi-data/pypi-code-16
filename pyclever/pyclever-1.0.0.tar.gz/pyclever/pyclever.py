from os.path import abspath
from subprocess import PIPE, Popen


def read_file(file_name):
    with open(abspath(file_name)) as f:
        return f.read()


class Cleverbot:
    def __init__(self, api_user, api_key, session=''):
        self.api_user = api_user
        self.api_key = api_key
        self.session = session

    def say(self, string):
        js_temp = read_file('template.js').replace('\n', ' ')
        js_temp = js_temp.format(API_USER=self.api_user, API_KEY=self.api_key, SESSION=self.session, STRING=string)
        cmd = "echo '{js_temp}' | node".format(js_temp=js_temp)
        response = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
        return response.decode('utf-8')[:-1]
