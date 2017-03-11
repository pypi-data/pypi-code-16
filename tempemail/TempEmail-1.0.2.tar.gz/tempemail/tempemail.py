from datetime import datetime
from json import loads
from random import choice, randint
from string import ascii_lowercase, digits

from websocket import create_connection


class Mailbox:
    def __init__(self):
        super(Mailbox, self).__init__()
        self.ws = create_connection("wss://dropmail.me/websocket")
        self.next = self.ws.recv
        self.close = self.ws.close
        self.address = self.next()[1:].split(":")[0]
        self.emails = []
        self.next()

    def __str__(self):
        str_emails = []
        for i in self.emails:
            str_emails.append(str(i))
        return str(str_emails)

    def __add_email(self, email):
        self.emails.append(email)

    def run(self):
        result = self.next()
        info_dict = loads(result[1:])
        info_dict['received'] = datetime.now()
        self.add_email(__Email(info_dict))

    def get_alt_address(self):
        pre_addr = self.address.split('@')[0]
        symbol = choice(['-', '.', '+'])
        first_let = ''.join([choice(ascii_lowercase + digits) for _ in range(randint(5, 10))])
        sec_let = ''.join([choice(ascii_lowercase + digits) for _ in range(randint(5, 10))])
        post_addr = self.address.split('@')[1]
        return '{pre_addr}{symbol}{first_let}@{sec_let}.{post_addr}'.format(pre_addr=pre_addr, symbol=symbol,
                                                                            first_let=first_let, sec_let=sec_let,
                                                                            post_addr=post_addr)


class __Email:
    def __init__(self, info_dict):
        self.info = info_dict

    def __str__(self):
        return self.info['subject']


if __name__ == '__main__':
    import sys
    from subprocess import call

    box = Mailbox()
    try:
        call(["echo '{0}' | pbcopy".format(box.address)], shell=True)
        print(box.address + " was copied to clipboard")
        print('Alternate: ' + box.get_alt_address())
        while True:
            box.run()
            print(box)
    except KeyboardInterrupt:
        box.close()
        sys.exit(0)
