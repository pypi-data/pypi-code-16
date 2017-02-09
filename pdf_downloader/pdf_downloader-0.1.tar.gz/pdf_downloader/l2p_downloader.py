import sys
import urlparse
import urllib2
import re
import os
from ntlm import HTTPNtlmAuthHandler


PROGRESSBAR_LENGTH = 40


def _cool_progress(text_to_append, current, total):
    if current > total:
        current = total
    progress = 0 if total == 0 else int(PROGRESSBAR_LENGTH*current/total)
    description = 'Starting...' if current == 0 else ('Done.' if current == total else 'Working...')

    # Make sure to overwrite the whole progress bar
    print '\r' + text_to_append + ' ' * (PROGRESSBAR_LENGTH - len(text_to_append) + 15)
    print '[' + '=' * progress + ' ' * (PROGRESSBAR_LENGTH-progress) + '] ' + description,


def download_pdfs(host, path, user, password):
    # Target folder
    if not os.path.exists('./pdfs/'):
        os.makedirs('./pdfs')

    # Password manager
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None, host + path, user, password)

    # Create the NTLM authentication handler
    auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)

    # Create and install the opener (= handler)
    opener = urllib2.build_opener(auth_NTLM)
    urllib2.install_opener(opener)

    # retrieve the result
    response = urllib2.urlopen(host + path)
    text = response.read()

    # Find all .pdf's, keep the relative path only (That's what the "(...)" is for)
    pdfs = re.findall(r'href=\"(/[\w\-/]+\.pdf)\"', text)

    # Download them all to ./pdfs/
    _cool_progress('Downloaded:', 0, 100)

    total = len(pdfs)
    current = 0
    for pdf in pdfs:
        current += 1

        # Authorize for new url, get response
        passman.add_password(None, host + pdf, user, password)
        response = urllib2.urlopen(host + pdf)

        # Find a sensible name
        name = re.findall(r'[\w_-]+\.pdf', pdf)[0]
        _cool_progress(' > ' + name, current, total)

        # Write to PDF ([w]rite [b]inary)
        myfile = open('./pdfs/' + name, 'wb')
        myfile.write(response.read())
        myfile.close()

    _cool_progress('Total: ' + str(total) + ' files', 100, 100)


# url [-u "username" [-p "password"]]
if __name__ == '__main__':

    user = ''
    password = ''
    path = ''
    host = ''

    next_is_user = False
    next_is_password = False

    for i in range(1, len(sys.argv)):
        if next_is_user:
            user = str(sys.argv[i])
            next_is_user = False
            next_is_password = False

        elif next_is_password:
            password = str(sys.argv[i])
            next_is_user = False
            next_is_password = False

        elif str(sys.argv[i]) == '-u' or str(sys.argv[i]) == '--u' \
                or str(sys.argv[i]) == '-user' or str(sys.argv[i]) == '--user':
            next_is_user = True
            next_is_password = False

        elif str(sys.argv[i]) == '-p' or str(sys.argv[i]) == '--p' \
                or str(sys.argv[i]) == '-password' or str(sys.argv[i]) == '--password':
            next_is_password = True
            next_is_user = False

        else:
            url = urlparse.urlparse(str(sys.argv[i]))
            host = url[0] + '://' + url[1]
            path = url[2]

    download_pdfs(host, path, user, password)
