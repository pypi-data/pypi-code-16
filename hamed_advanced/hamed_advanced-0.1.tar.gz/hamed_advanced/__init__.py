#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from collections import OrderedDict
import datetime

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"


def get_code(dt, cercle_id):
    ''' Fixed string version of transmitted info

        {cercle:3}{year:2}{month:2}{day:2} '''
    return "{cercle}{year}{month}{day}".format(
        cercle=cercle_id,
        year=str(dt.year)[2:],
        month=str(dt.month).zfill(2),
        day=str(dt.day).zfill(2))


def get(l, index, pad):
    ''' Character from alphabet at requested position, moved by pad '''
    if not index <= len(l) - 1:
        raise ValueError("'{}' not an index of the list".format(index))
    pad = abs(pad)
    ni = index + pad
    lli = len(l) - 1
    if ni > lli:
        ni = ni - lli
    if ni < 0:
        ni = lli + ni
    return l[ni]


def deget(l, letter, pad):
    ''' Index in alphabet for letter after pad correction '''
    try:
        index = l.index(letter)
    except ValueError:
        return None
    ni = index - abs(pad)
    lli = len(l) - 1
    if ni > lli:
        ni = ni - lli
    if ni < 0:
        ni = lli + ni
    return ni


def cipher(text, pad):
    ''' Encode text with caesar cipher for pad '''
    chars = []
    for c in text:
        try:
            chars.append(get(alphabet, alphabet.index(c), pad))
        except:
            chars.append(c)
    return "".join(chars)


def decipher(text, pad):
    ''' Decode text with caesar cipher for pad '''
    chars = []
    for c in text:
        ci = deget(alphabet, c, pad)
        if ci is not None:
            chars.append(alphabet[ci])
        else:
            chars.append(c)
    return "".join(chars)


def get_doy(date):
    ''' Day of the year for specified date, a a 3-chars long string '''
    return str(date.timetuple().tm_yday).zfill(3)


def get_adavanced_request_code(cercle_id, date=None):
    ''' Usable request code for a specified datetime or today '''
    date = datetime.datetime.now() if date is None else date
    alpha_pad = alphabet[date.hour]
    code = get_code(date, cercle_id)
    return "{pad}{ecode}".format(
        pad=alpha_pad,
        ecode=cipher(code, date.hour)).upper()


def decode_request_code(code):
    ''' Decoded information from a request code '''
    code = code.lower()
    alpha_pad = code[0]
    ciphered = code[1:]
    pad = alphabet.index(alpha_pad)
    text = decipher(ciphered, pad)
    cercle_id = text[0:2]
    year = int("20{}".format(text[2:4]))
    month = int(text[4:6])
    day = int(text[6:8])
    date = datetime.date(year, month, day)
    return cercle_id, date, pad


def get_acception_code(request_code):
    ''' Acceptation code for a request_code '''
    cercle_id, date, pad = decode_request_code(request_code)
    return cipher(
        "{doy}{cercle}".format(doy=get_doy(date),
                               cercle=cercle_id), pad).upper()


def validate_acceptation_code(request_code, acceptation_code):
    ''' Boolean whether acceptation_code and request_code matches '''
    acceptation_code = acceptation_code.lower()
    try:
        assert len(request_code) == 9
        assert len(acceptation_code) == 5
        req_cercle_id, date, pad = decode_request_code(request_code)
        text = decipher(acceptation_code, pad)
        doy = text[:3]
        cercle_id = text[3:]
        assert req_cercle_id == cercle_id
        assert doy == get_doy(date)
    except:
        return False
    else:
        return True


def main():
    import sys

    ACCEPT, REQUEST, VALID, HELP, EXIT = ('accept', 'request', 'valid',
                                          'help', 'exit')
    actions = OrderedDict([
        (REQUEST, "Generate a Request Code"),
        (ACCEPT, "Get an Acceptation Code from a request Code"),
        (VALID, "Validate an Acceptation Code for a Request Code"),
        (HELP, "Display Options"),
        (EXIT, "Quit"),
    ])

    def fail(message):
        print(message)
        sys.exit(1)

    action = HELP
    if len(sys.argv) > 1:
        if sys.argv[1].strip().lower() in actions.keys():
            action = sys.argv[1].strip().lower()

    def do_request():
        print("Obtaining a RequestCode for a simulated Cercle")
        cercle_id = input("Please provide a 2chars-long `cercle_id`: ")
        try:
            assert len(cercle_id) == 2
            assert cercle_id.isdigit()
        except Exception as exp:
            fail("ERROR. Incorrect cerle_id: {}".format(exp))

        date_str = input("Please provide a Request Date in Y-M-D format "
                         "(or blank for toay): ")
        try:
            date = datetime.datetime.now() if not len(date_str) else \
                datetime.datetime(*[int(p) for p in date_str.split('-')],
                                  hour=12)
        except Exception as exp:
            fail("ERROR. Invalid Date Format: {}".format(exp))

        try:
            code = get_adavanced_request_code(cercle_id=cercle_id, date=date)
        except Exception as exp:
            fail("ERROR. Incorrect input: {}".format(exp))
        else:
            print("Request Code for",
                  "Cercle", cercle_id, "at", date, "---", code)

    def do_accept():
        print("Obtaining an AcceptationCode for a specified RequestCode")
        code = input("Please provide a RequestCode: ")
        try:
            cercle_id, date, pad = decode_request_code(code)
        except Exception as exp:
            fail("ERROR. Invalid RequestCode: {}".format(exp))
        else:
            print("RequestCode OK",
                  "Cercle", cercle_id, "Date", date, "Pad", pad)

        acceptation_code = get_acception_code(code)
        print("Acceptation Code for", code, "---", acceptation_code)

    def do_valid():
        print("Verifying that an AcceptationCode is valid for a RequestCode")
        request_code = input("Please provide a RequestCode: ")
        acceptation_code = input("Please provide an AcceptationCode: ")
        try:
            assert validate_acceptation_code(request_code, acceptation_code)
        except Exception as exp:
            print("FAILURE. RequestCode and AcceptationCode do NOT match. {}"
                  .format(exp))
        else:
            print("SUCCESS. RequestCode and AcceptationCode matches.")

    def do_help():
        print("Please section an action:")
        for index, label in enumerate(actions.values()):
            print("{}.  ".format(index + 1), label)
        input_index = input("What do you want to do? [{}-{}] "
                            .format(1, len(actions)))
        try:
            action = list(actions.keys())[int(input_index) - 1]
        except Exception as exp:
            fail("ERROR. You must enter the action's number. {}".format(exp))
        else:
            start_action(action)

    def do_exit():
        sys.exit(0)

    processes = {
        ACCEPT: do_accept,
        REQUEST: do_request,
        VALID: do_valid,
        HELP: do_help,
        EXIT: do_exit,
    }

    def start_action(action):
        if action in processes.keys():
            processes.get(action)()
            print("\n---\n")
            start_action(HELP)

    title = "RAMEDCollect (hamed) Advanced-mode Request Manager"
    print(title)
    print("".join(["-" for _ in range(len(title))]))
    print("")
    start_action(action)

if __name__ == '__main__':
    main()
