import requests
from .Updater import Updater
from .MessageResponse import MessageResponse


class UpdateHandler:
    def __init__(self):
        self.update = None

    def send_response(self, room, response):  # Todo: move API calls t subclass
        if type(response) is MessageResponse:
            requests.post(
                Updater.API_URL + 'messages',
                headers=Updater.HEADERS,
                data={
                    'roomId': room,
                    'markdown': response.get_plain_text()
                }
            )
        else:
            raise Exception("not implemented yet")

    def send_response_by_email(self, email, response):  # Todo: move API calls t subclass
        if type(response) is MessageResponse:
            requests.post(
                Updater.API_URL + 'messages',
                headers=Updater.HEADERS,
                data={
                    'toPersonEmail': email,
                    'markdown': response.get_plain_text()
                }
            )
        else:
            raise Exception("not implemented yet")
