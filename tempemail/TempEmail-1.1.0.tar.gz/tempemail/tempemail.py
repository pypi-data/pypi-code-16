from datetime import datetime
from json import loads
from random import choice, randint
from string import ascii_lowercase, digits

from websocket import create_connection
from urllib.request import urlopen


class Mailbox:
    def __init__(self):
        super(Mailbox, self).__init__()
        self.ws = create_connection("wss://dropmail.me/websocket")
        self.next = self.ws.recv
        self.close = self.ws.close
        self.address = self.next()[1:].split(":")[0]
        self.emails = []
        self.next()

    def __repr__(self):
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
        self.__add_email(Email(info_dict))

    def get_alt_address(self):
        pre_addr = self.address.split('@')[0]
        symbol = choice(['-', '.', '+'])
        first_let = ''.join([choice(ascii_lowercase + digits) for _ in range(randint(5, 10))])
        sec_let = ''.join([choice(ascii_lowercase + digits) for _ in range(randint(5, 10))])
        post_addr = self.address.split('@')[1]
        return '{pre_addr}{symbol}{first_let}@{sec_let}.{post_addr}'.format(pre_addr=pre_addr, symbol=symbol,
                                                                            first_let=first_let, sec_let=sec_let,
                                                                            post_addr=post_addr)

    def get_email_data(self, email_index):
    	ref = self.emails[email_index].info['ref']
    	pre_addr = self.address.split('@')[0]
    	post_addr = self.address.split('@')[1]
    	url = 'https://dropmail.me/download/mail/{pre_addr}%40{post_addr}/{ref}'.format(pre_addr=pre_addr, 
    																					post_addr=post_addr,
    																					ref=ref)
    	email_data = urlopen(url).read()
    	return email_data


class Email:
    def __init__(self, info_dict):
        self.info = info_dict

    def __repr__(self):
        return self.info['subject']

if __name__ == '__main__':
    box = Mailbox()
    print(box.address)
