import time
from random import choice
from string import ascii_lowercase, ascii_letters, digits, punctuation

from subprocess import Popen, PIPE
from tempemail import Mailbox

__author__ = 'sonar235'


def megareg():
	cmd = "megareg --register -n '{name}' -e '{email}' -p '{password}'"
	box = Mailbox()
	chars = ascii_letters + digits + punctuation
	name = 'John Smith'
	email = box.address
	password = ''.join([choice(chars) for _ in range(16)])
	cmd = cmd.format(name=name, email=email, password=password.replace("'", "\\'"))
	verify_cmd = Popen(cmd, shell=True, stdout=PIPE).communicate()[0].decode()
	verify_cmd = verify_cmd.split('you must run:\n\n  ')[1]
	verify_cmd = verify_cmd.split('@LINK@')[0] + "'{confirmation_link}'"
	box.run()
	email_data = box.get_email_data(0).decode()
	confirmation_link = email_data.split('to confirm your MEGA account:')[1]
	confirmation_link = confirmation_link.split('Best regards')[0]
	confirmation_link = confirmation_link.split('\r\n\r\n')[1]
	verify_cmd = verify_cmd.format(confirmation_link=confirmation_link)
	Popen(verify_cmd, shell=True, stdout=PIPE)
	return email, password


if __name__ == '__main__':
    print(megareg())
