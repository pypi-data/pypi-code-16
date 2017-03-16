# -*- coding: UTF-8 -*-
from bir_api import NAMESPACES, COMPANY_FIELD_MAP, DETAILED_REPORT_NAMES_MAP
from bir_api.conf import GUS_KEY, GUS_URL
from bir_api.envelopes import LOGIN_ENVELOPE, LOGOUT_ENVELOPE, SEARCH_ENVELOPE, FULL_REPORT_ENVELOPE
from congo.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from lxml import etree, objectify
from requests.exceptions import ConnectionError
import email
import re
import requests

def get_message_element(message, payload_num, path):
    resp = message.get_payload(payload_num).get_payload(decode = True)
    return etree.fromstring(resp).xpath(path, namespaces = NAMESPACES)

@python_2_unicode_compatible
class Company(object):
    name = None
    vat_no = None
    regon = None
    krs = None
    street = None
    zip_code = None
    city = None
    country = None
    voivodeship = None
    county = None
    community = None
    type = None

    def __str__(self):
        return u"%s (%s)" % (self.name, self.vat_no)

    @classmethod
    def get_from_bir(cls, vat_no = None, regon = None, krs = None, detailed = False):
        company_dict = {}

        vat_no = str(vat_no).lower().replace('-', '').replace(' ', '').replace('pl', '') if vat_no else None
        regon = str(regon).lower().replace('-', '').replace(' ', '') if regon else None
        krs = str(krs).lower().replace('-', '').replace(' ', '') if krs else krs

        try:
            gus_key = GUS_KEY
            gus_url = GUS_URL
            api = RegonApi(gus_url)
            api.login(gus_key)
            gus_result = api.search(nip = vat_no, regon = regon, krs = krs, detailed = detailed)
            api.logout()

            if gus_result:
                obj = cls()
                obj.country = "PL"

                for x, y in COMPANY_FIELD_MAP:
                    setattr(obj, y, getattr(gus_result, x, None))
                return obj

        except ConnectionError:
            pass

        return company_dict

    @classmethod
    def search_in_bir(cls, vat_no_list = [], regon_list = [], krs_list = [], detailed = False):
        raise NotImplementedError


class RegonApiError(RuntimeError):
    pass

class RegonApi(object):
    def __init__(self, service_url):
        self.service_url = service_url
        self.sid = None

    def call(self, envelope, **args):
        '''
        Calls an API's method (descibed by the envelope)     
        '''
        data = envelope.format(api = self, **args)
        res = requests.post(
            self.service_url,
            stream = True,
            data = data,
            headers = {
                'Content-Type': 'application/soap+xml; charset=utf-8',
                'sid': self.sid
            }
        )
        mimemsg = '\r\n'.join('{0}: {1}'.format(key, val) for key, val in res.headers.items())
        mimemsg += '\r\n' + res.text.encode('UTF-8')

        mesg = email.message_from_string(mimemsg)
        assert mesg.is_multipart, 'Response is not multipart.'

        return mesg

    def login(self, user_key):
        '''
        Logs in to the REGON API Service (uses API key provided by the REGON administrators)
        '''
        mesg = self.call(LOGIN_ENVELOPE, user_key = user_key)

        result = get_message_element(mesg, 0, '//bir:ZalogujResult/text()')
        if not result:
            self.sid = None
            raise RegonApiError('Login failed.')

        self.sid = result[0]

        return self.sid

    def logout(self):
        '''
        Ends API session
        '''
        if not self.sid:
            raise RegonApiError('Not logged in.')

        mesg = self.call(LOGOUT_ENVELOPE)
        result = get_message_element(mesg, 0, '//bir:WylogujResult/text()')

        if not result or result[0] != 'true':
            raise RegonApiError('Logout failed.')

        return True

    def search(self, nip = None, regon = None, krs = None, nips = None, regons = None, krss = None, detailed = False):
        if not (regon or nip or krs or regons or nips or krss):
            raise RegonApiError('You have to pass at least one of: nip(s), regon(s) or krs(s) parameters.')

        param = ''
        if nip:
            param += '<dat:Nip>{0}</dat:Nip>'.format(nip)

        if regon:
            param += '<dat:Regon>{0}</dat:Regon>'.format(regon)

        if krs:
            param += '<dat:Krs>{0}</dat:Krs>'.format(krs)

        if nips:
            nip_str = ''.join(nips)
            assert len(nip_str) % 10 == 0, 'All NIPs should be 10 character strings.'

            param += '<dat:Nipy>{0}</dat:Nipy>'.format(nip_str)

        if krss:
            krs_str = ''.join(krss)
            assert len(krs_str) % 10 == 0, 'All KRSs should be 10 character strings.'
            param += '<dat:Krsy>{0}</dat:Krsy>'.format(krs_str)

        if regons:
            regons_str = ''.join(regons)
            rl = len(regons_str)

            if rl % 9 == 0:
                param += '<dat:Regony9zn>{0}</dat:Regony9zn>'.format(regons_str)
            elif rl % 14 == 0:
                param += '<dat:Regony14zn>{0}</dat:Regony14zn>'.format(regons_str)
            else:
                raise AssertionError('All REGONs should be either 9 or 14 character strings.')

        mesg = self.call(SEARCH_ENVELOPE, param = param)
        result = get_message_element(mesg, 0, '//bir:DaneSzukajResult/text()')

        if not result:
            return None

        search_results = objectify.fromstring(result[0]).dane

        if not detailed:
            return search_results
        else:
            detailed_data = []
            for rs in search_results:

                # Sometimes the leading zeros get lost
                correct_regon = '{0:014}'.format(int(rs.Regon)) if len(str(rs.Regon)) not in (9, 14) else rs.Regon

                correct_report_name = DETAILED_REPORT_NAMES_MAP.get(str(rs.SilosID))
                rs.detailed = self.full_report(correct_regon, correct_report_name)

                if rs.Typ == 'F':
                    # Data from sole proprietorhsips has to be extended by a additional report
                    sp_data = self.full_report(correct_regon, 'PublDaneRaportFizycznaOsoba')
                    rs.detailed.extend(sp_data.getchildren())

                detailed_data.append(rs)

            return detailed_data

    def full_report(self, regon, report_name):
        mesg = self.call(FULL_REPORT_ENVELOPE, regon = regon, report_name = report_name)

        try:
            result = objectify.fromstring(get_message_element(mesg, 0, '//bir:DanePobierzPelnyRaportResult/text()')[0])
        except IndexError:
            result = []

        if not result:
            raise RegonApiError('Getting full report failed.')

        return result[0].dane
