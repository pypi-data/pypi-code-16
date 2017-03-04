#!/usr/bin/python3
# coding: utf8
"""Get the french train schedules and its states, send SMS and send alert or text to Domoticz."""
import sys
import os
import xml.etree.ElementTree as ET
from urllib.parse import quote
from urllib.error import URLError, HTTPError
import urllib.request
import argparse
import configparser

__all__ = ['transilien']


def get_train_infos(host_api, login, password, gare, depart):
    """Retrieve the data provided by the SNCF API.

    :param host_api: Host of the SNCF API, protocol (HTTP or HTTPS) more an IP or a domain name.
    :type host_api: str

    :param login: Login for the SNCF API.
    :type login: str

    :param password: Password for the SNCF API.
    :type password: str

    :param gare: Code UIC of the departure train station.
    :type gare: int

    :param depart: Code UIC of the arrival train station.
    :type depart: int

    :returns: XML of the response of the API otherwise an error message.
    :rtype: str
    """
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    url = str(host_api) + '/gare/' + str(gare) + '/depart/' + str(depart) + '/'
    password_mgr.add_password(realm=None, uri=url, user=str(login), passwd=str(password))
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    opener = urllib.request.build_opener(auth_handler)
    try:
        opener.open(url)
        urllib.request.install_opener(opener)
        with urllib.request.urlopen(url) as response:
            return response.read()
    except HTTPError as e:
        error_message = str(e) + ' : ' + str(e.read())
        return error_message
    except URLError as e:
        error_message = str(e)
        return error_message
    except ValueError as e:
        error_message = str(e)
        return error_message


def format_content(nbr_trains, content, name_station):
    """Format the data provided by the SNCF API.

    :param nbr_trains: Number of trains to format.
    :type nbr_trains: int

    :param content: Data provided by the SNCF API (XML).
    :type content: str

    :param name_station: Name of the departure train station.
    :type name_station: str

    :returns: Formatted text.
    :rtype: list

    :returns: State to true if the train is delayed or deleted.
    :rtype: bool
    """
    nbr = 1
    values = []
    state = False
    no_train = True
    if isinstance(content, int):
        return ["Problem with content , can't be a int"], False
    if not isinstance(nbr_trains, int):
        nbr_trains = 1
    try:
        content = ET.fromstring(content)
    except ET.ParseError as e:
        return ["ParseError : " + str(e.msg)], False
    for train in content.findall('train'):
        try:
            no_train = False
            etat = train.find('etat').text
            values.append(str(name_station) + '_:_' + train[0].text.replace(" ", "_") + '_' + etat)
            state = True
        except AttributeError:
            values.append(str(name_station) + '_:_' + train[0].text.replace(" ", "_"))
        nbr = nbr + 1
        if nbr > nbr_trains:
            break
    if no_train:
        return ["No train"], True
    return values, state


def send_alert_to_domoticz(host, port, idx, values, level):
    """Send alert to a virtual device in Domoticz.

    :param host: Host of the Domoticz server, an IP or a domain name.
    :type host: str

    :param port: Port of the Domoticz server.
    :type port: int

    :param idx: Identifier of the virtual device in Domoticz.
                (can be found in the devices tab in the column “IDX”).
    :type idx: int

    :param values: List of values returned by format function.
    :type values: list

    :param level: Level = (0=gray, 1=green, 2=yellow, 3=orange, 4=red).
    :type level: int

    :returns: The return value of Domoticz.
    :rtype: str
    """
    try:
        int(port)
    except ValueError:
        return 'Problem with port number'
    value = ""
    if not values:
        return 'Problem with values: Empty'
    elif isinstance(values, (list, tuple)):
        for item in values:
            value = value + item + ' '
    else:
        return 'Problem with values: need to be a list or a tuple'
    url = 'http://' + str(host) + ':' + str(port) + '/json.htm?type=command&param=udevice&idx=' \
          + str(idx) + '&nvalue=' + str(level) + '&svalue=' + quote(value.encode('utf8'))
    try:
        response = urllib.request.urlopen(url)
    except URLError as e:
        return 'Failed to reach a serverReason: ' + str(e.reason)
    else:
        return response.read()


def send_text_to_domoticz(host, port, idx, values):
    """Send text to a virtual device in Domoticz.

    :param host: Host of the Domoticz server, an IP or a domain name.
    :type host: str

    :param port: Port of the Domoticz server.
    :type port: int

    :param idx: Identifier of the virtual device in Domoticz.
        (can be found in the devices tab in the column “IDX”)
    :type idx: int

    :param values: List of values returned by format function.
    :type values: list

    :returns: the return value of Domoticz.
    :rtype: str
    """
    try:
        int(port)
    except ValueError:
        return 'Problem with port number'
    value = ""
    if not values:
        return 'Problem with values: Empty'
    elif isinstance(values, (list, tuple)):
        for item in values:
            value = value + item + ' '
    else:
        return 'Problem with values: need to be a list or a tuple'
    url = 'http://' + str(host) + ':' + str(port) + '/json.htm?type=command&param=udevice&idx=' \
          + str(idx) + '&nvalue=0&svalue=' + quote(value.encode('utf8'))
    try:
        response = urllib.request.urlopen(url)
    except URLError as e:
        return 'Failed to reach a serverReason: ' + str(e.reason)
    else:
        return response.read()


def valid_number(phone_number):
    """Valid a cellphone number.

    :param phone_number: Cellphone number.
    :type phone_number: str

    :returns: true if it's a valid cellphone number.
    :rtype: bool
    """
    phone_number = phone_number.replace(" ", "")
    if len(phone_number) != 10:
        return False
    for i in range(10):
        try:
            int(phone_number[i])
        except ValueError:
            return False
    return True


def send_sms(host, port, password, number, values):
    """Send SMS to a list of cellphone number.

    :param host: Host of the SMS gateway, can be an IP or a domain name.
    :type host: str

    :param port: Port of the SMS gateway.
    :type port: int

    :param password: Password for the SMS gateway.
    :type password: str

    :param number: List of cellphone number.
    :type number: list

    :param values: List of values returned by format function.
    :type values: list

    :returns: the return value of the SMS gateway.
    :rtype: str
    """
    try:
        int(port)
    except ValueError:
        return 'Problem with port number'
    value = ""
    return_value = []
    if not values:
        return 'Problem with values: Empty'
    elif isinstance(values, (list, tuple)):
        for item in values:
            value = value + item + ' '
    else:
        return 'Problem with values: need to be a list or a tuple'
    for num in number:
        num = num.replace(" ", "")
        if not valid_number(num):
            return "Invalid mobile number: " + str(num)
        url = 'http://' + str(host) + ':' + str(port) + '/sendsms?phone=' + str(num) + '&text=' \
              + quote(value) + '&password=' + str(password)
        try:
            response = urllib.request.urlopen(url)
        except HTTPError as e:
            return 'Request Error code: ' + str(e.code)
        except URLError as e:
            return 'Failed to reach a serverReason: ' + str(e.reason)
        else:
            return_value.append(response.read())
    return return_value


def transilien():
    """Main function."""
    config_name = "conf.cfg"
    config_file = os.path.join(os.path.dirname(__file__), config_name)
    config = configparser.ConfigParser()
    config.read(config_file)

    host_api = config["api"]["host"]
    login = config["api"]["login"]
    password = config["api"]["password"]
    host = config["domoticz"]["host"]
    port = config["domoticz"].getint('port')
    idx_alert = config["domoticz"]["idx_alert"]
    idx_text = config["domoticz"]["idx_text"]
    level = config["domoticz"]["level"]
    host_sms = config["sms"]["host"]
    port_sms = config["sms"].getint('port')
    password_sms = config["sms"]["password"]
    number = config["sms"]["number"].split(',')

    parser = argparse.ArgumentParser()
    parser.add_argument("--nbrTrains",
                        help="the number of trains to check",
                        type=int,
                        default=config["default"]["nbrTrains"])
    parser.add_argument("--depart",
                        help="the departure's station  number ",
                        default=config["default"]["depart"])
    parser.add_argument("--gare",
                        help="the arrival's station  number ",
                        default=config["default"]["gare"])
    parser.add_argument("--sendSMS",
                        help="send a SMS",
                        action='store_true',
                        default=config['default'].getboolean('sendSMS'))
    parser.add_argument("--departName",
                        help="the departure's station  name ",
                        default=config["default"]["departName"])
    parser.add_argument("--gareName",
                        help="the arrival's station  name ",
                        default=config["default"]["gareName"])
    parser.add_argument("--alert",
                        help="check if trains have state",
                        action='store_true',
                        default=config['default'].getboolean('alert'))
    parser.add_argument("--v", help="verbose",
                        action='store_true',
                        default=config['default'].getboolean('verbose'))
    args = parser.parse_args()

    depart = args.depart
    gare = args.gare
    nbr_trains = args.nbrTrains
    depart_name = args.departName
    gare_name = args.gareName
    alert = args.alert
    verbose = args.v
    send_sms_value = args.sendSMS

    if alert:
        content = get_train_infos(host_api, login, password, gare, depart)
        if verbose:
            print(content)
        values, state = format_content(nbr_trains, content, depart_name)
        if verbose:
            print(values)
            print("state : " + str(state))
        if state:
            response = send_alert_to_domoticz(host, port, idx_alert, values, level)
            if verbose:
                print(response)
            if send_sms_value:
                response = send_sms(host_sms, port_sms, password_sms, number, values)
                if verbose:
                    print(response)
    else:
        go_content = get_train_infos(host_api, login, password, gare, depart)
        if verbose:
            print(go_content)
        ret_content = get_train_infos(host_api, login, password, depart, gare)
        if verbose:
            print(ret_content)
        values = format_content(nbr_trains, go_content, depart_name)[0] + format_content(nbr_trains, ret_content, gare_name)[0]
        if verbose:
            print(values)
        response = send_text_to_domoticz(host, port, idx_text, values)
        if verbose:
            print(response)
            print("send SMS : " + str(send_sms_value))
        if send_sms_value:
            response = send_sms(host_sms, port_sms, password_sms, number, values)
            if verbose:
                print(response)
    sys.exit(0)


if __name__ == "__main__":
    transilien()
