import urllib.request


class Camera:
    def start(self):
        self.__http_request("http://10.5.5.9/gp/gpControl/command/shutter?p=1")

    def stop(self):
        self.__http_request("http://10.5.5.9/gp/gpControl/command/shutter?p=0")

    def __http_request(self, address):
        return urllib.request.urlopen(address).read()
