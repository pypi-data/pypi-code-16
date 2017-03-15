import time

class Config:
    def __init__(self, conf_list):
        for property in conf_list:
            if 'name' in property:
                self.name = property['name']
            else:
                self.name = 'XMLTest_' + str(time.time())

            if 'timeout' in property:
                self.timeout = property['timeout']
            else:
                self.timeout = 6000  # Default Timeout = 6 secs

    def get_name(self):
        return self.name

    def get_timeout(self):
        return self.timeout
