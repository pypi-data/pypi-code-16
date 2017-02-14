# -*- coding: utf-8 -*-

import requests
import json
from oe_geoutils import AdminGrenzenClient
from requests.exceptions import RequestException
from oe_daemonutils.dossierservice.utils import text_


class DaemonException(Exception):
    """
    Common Daemon Exception
    Daemon stops with working
    """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.message = msg


class MasterdataNotFoundException(Exception):
    def __init__(self, data_uri):
        self.data_uri = data_uri

    def __str__(self):
        return "MasterdataNotFoundException: not found for url: {0}".format(self.data_uri)


class DossierService(object):

    def __init__(self, settings, logger, system_token):
        """
        Service which can be used for processing a feed entry to a dossier

        :param settings: daemon settings
        :param logger: logger object
        :param system_token: token for authentication in rest requests
        """
        self.settings = settings
        self.logger = logger
        self.system_token = system_token
        self.admin_grenzen_client = AdminGrenzenClient(base_url=settings.get('daemon.administratievegrenzen.url'))
        self.regioverantwn_url = settings.get('daemon.regioverantwoordelijken.url')
        self.headers = {'OpenAmSSOID': self.system_token, 'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def create_dossier(self, entry, notifications_dict):
        """
        abstract method for creating a dossier

        :param entry: atom feed entry
        :param notifications_dict: dict with actors who must be notified about the created dossiers
        """
        pass

    def _check_response_state(self, response):
        if 400 <= response.status_code < 500:
            self.logger.error(response.text)
            msg = 'Client Error ({0}) for url: {1} {2}'.format(response.status_code, response.request.method,
                                                               response.url)
            self.logger.error(msg)

            raise DaemonException(msg)
        elif 500 <= response.status_code < 600:
            self.logger.error(response.text)
            msg = 'Server Error ({0})  for url: {1} {2}'.format(response.status_code, response.request.method,
                                                                response.url)
            self.logger.error(msg)
            raise DaemonException(msg)
        else:
            return True

    def _get_data(self, data_uri):
        """
        Get the json data of the uri

        :param data_uri: uri
        :return: json data
        """
        data_response = requests.get(data_uri, headers=self.headers)
        self._check_response_state(data_response)
        return json.loads(text_(data_response.content))

    def _get_master_data(self, data_uri):
        """
        Get the json data of the uri

        :param data_uri: uri
        :return: json data
        :return: raise MasterdataNotFoundException when request raises a Not Found exception
        """
        data_response = requests.get(data_uri, headers=self.headers)
        if data_response.status_code == 404:
            raise MasterdataNotFoundException(data_uri)
        else:
            data_response.raise_for_status()
        return json.loads(text_(data_response.content))

    def _determine_niscodes(self, geojson, types):
        """
        Get administrative area information of the given geojson.
        If the geojson overlaps multiple administrative areas

        :param geojson: contour geojson
        :param types: array, return types of administrative areas ['gemeente', 'provincie']
        :return: adminstative area information
        """
        results = []
        if 'gemeente' in types:
            results.append(self.admin_grenzen_client.get_gemeente(geojson))
        if 'provincie' in types:
            results.append(self.admin_grenzen_client.get_provincie(geojson))
        niscodes = [result['niscode'] for result in results]
        return niscodes

    def _determine_region_reps(self, niscodes, discipline=None, process=None):
        """
        Get the region reps given the area niscodes

        :param niscodes: list of niscodes
        :param discipline: discipline for the representatives
        :param process: for specific process
        :return: list of actor objects each having a "actor" attribute including the actor_uri
        """
        params = {'niscode': niscodes}
        if process:
            params["proces"] = process
        if discipline:
            params["discipline"] = discipline
        res = requests.get(
            self.regioverantwn_url,
            params=params,
            headers=self.headers
        )
        res.raise_for_status()
        return json.loads(res.text)

    def _get_emails_actoren(self, actors):
        """
        Get the email addresses of the actors given the actor_uris.
        Preference is given to the work e-mail addresses.

        :param actors: actor objects (bv [{'id': 'http//id.erfgoed.net/actoren/1'}])
        :return:
        """
        emails = [self._get_actor_email(actor["actor"]) for actor in actors]
        return [email for email in emails if email]

    def _get_actor_email(self, actor_uri):
        """
        Get the email of the actor given the actor_uri.
        Preference is given to the work e-mail address.

        :param actor_uri: uri van de actor ('http//id.erfgoed.net/actoren/1')
        :return: string email address
        """
        try:
            res = requests.get(
                actor_uri,
                headers=self.headers
            )
            res.raise_for_status()
        except RequestException as e:
            self.logger.error(
                "Error: unable to send email to actor {0}: {1}".format(actor_uri, repr(e)))
            return None
        actor = json.loads(res.text)
        return next((email['email'] for email in actor.get('emails', []) if email.get('type', {}).get('id', None) == 2),
                    next((email['email'] for email in actor.get('emails', [])), None))
