# -*- coding: utf-8 -*-
import logging
from enum import Enum
from pprint import pformat
from types import SimpleNamespace

from requests import sessions

logging.basicConfig(format='%(message)s',
                    level=logging.INFO)

api_url = 'https://api.leaseweb.com/v1'

Method = Enum('Method', ['GET', 'POST'])


class VirtualServersAPI:
    vps_resource = '/virtualServers'

    def __init__(self, api_key, api_url=api_url):
        self.api_url = api_url
        self.api_key = api_key

        self.refresh()

        all_actions = {
            'poweron': lambda: self._all(self.poweron),
            'poweroff': lambda: self._all(self.poweroff),
            'reboot': lambda: self._all(self.reboot)
        }
        self.all = SimpleNamespace(**all_actions)

    def _api_call(self, method, resource):
        url = f'{self.api_url}{resource}'
        headers = {'X-Lsw-Auth': self.api_key}

        logging.info(url)

        with sessions.Session() as session:
            response_dict = session.request(
                method.name,
                url,
                headers=headers,
            ).json()

        logging.info(pformat(response_dict))

        return response_dict

    def refresh(self):
        self.virtual_servers = self._api_call(
            Method.GET, VirtualServersAPI.vps_resource)
        self.vps_ids = {
            vps['id'] for vps in self.virtual_servers['virtualServers']
        }

    def _all(self, action):
        for vps_id in self.vps_ids:
            action(vps_id)

    def poweroff(self, vps_id):
        self._api_call(
            Method.POST, f'{VirtualServersAPI.vps_resource}/{vps_id}/powerOff')

    def poweron(self, vps_id):
        self._api_call(
            Method.POST, f'{VirtualServersAPI.vps_resource}/{vps_id}/powerOn')

    def reboot(self, vps_id):
        self._api_call(
            Method.POST, f'{VirtualServersAPI.vps_resource}/{vps_id}/reboot')


def main():
    import argparse

    parser = argparse.ArgumentParser(description='CLI to Leaseweb API')
    group = parser.add_mutually_exclusive_group()

    parser.add_argument('-k', '--api-key', required=True,
                        help='API key retrieved from '
                        'https://secure.leaseweb.com/en/sscApi')
    group.add_argument('--poweron', action='store_true',
                       help='Poweron all virtual servers')
    group.add_argument('--poweroff', action='store_true',
                       help='Poweroff all virtual servers')
    group.add_argument('--reboot', action='store_true',
                       help='Reboot all virtual servers')
    args = parser.parse_args()

    vs = VirtualServersAPI(api_key=args.api_key)
    if args.poweron:
        vs.all.poweron()
    if args.poweroff:
        vs.all.poweroff()
    if args.reboot:
        vs.all.reboot()


if __name__ == '__main__':
    main()
