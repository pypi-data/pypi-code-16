from urllib.parse import urljoin

import requests

from django.conf import settings


class ApiError(BaseException):
    pass


class GlossaryService(object):

    register_url = urljoin(settings.GLOSSARY_SERVICE_URL, "/register-app")

    @classmethod
    def register(cls, update_url):
        r = requests.post(cls.register_url, {"update_url": update_url})
        print(cls.register_url)
        if r.status_code != 200:
            raise ApiError(
                "Ошибка при регистрации приложения. Код - {}"
                .format(r.status_code)
            )
        return r.json()["token"]
