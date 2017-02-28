# -*- coding: utf-8 -*-
import csv
import os
import sys
import getpass
import argparse
import tempfile

import lastpass
import requests
import urltools
from lastpass.exceptions import (
    LastPassIncorrectYubikeyPasswordError,
    LastPassIncorrectGoogleAuthenticatorCodeError,
)

DEFAULT_DOMAINS_LIST = 'https://raw.githubusercontent.com/pirate/sites-using-cloudflare/master/sorted_unique_cf.txt'


cf_domains = {}


def match_domains(account):
    parsed = urltools.parse(account.url)
    rootdom = "{domain}.{tld}".format(**parsed.__dict__)
    if rootdom in cf_domains:
        return rootdom


def domains_to_file(accounts, fobj, fields):
    print "Matching domains."
    writer = csv.DictWriter(fobj, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for account in accounts:
        if match_domains(account):
            writer.writerow(account.__dict__)
    print "Done."
    fobj.close()


def domains_to_stdout(accounts):
    print "Matching domains."
    matched_domains = []
    for acct in accounts:
        domain = match_domains(acct)
        if domain is not None:
            matched_domains.append(domain)
    if not matched_domains:
        print "No CloudFlare domains found in LastPass vault."
    else:
        print "The following (potentially) compromised CloudFlare domains " \
              "were found in your LastPass vault: "
        print "\n".join(sorted(matched_domains))


def make_dict(fobj):
    print "Reading CloudFlare domains list."
    global cf_domains
    for line in fobj.xreadlines():
        cf_domains[line.strip()] = None


def get_vault():
    print
    username = raw_input('LastPass Username: ').strip()
    passwd = getpass.getpass('LastPass Master Password: ')
    print "Logging into LastPass."
    try:
        return lastpass.Vault.open_remote(username, passwd)
    except (LastPassIncorrectYubikeyPasswordError,
            LastPassIncorrectGoogleAuthenticatorCodeError) as e:
        print
        twofa = raw_input('LastPass MFA Token: ').strip()
        return lastpass.Vault.open_remote(username, passwd, twofa)


def download_file(loc):
    print "Using CloudFlare domains list from %s." % loc
    sys.stdout.write("Downloading...")
    sys.stdout.flush()
    tmpf = tempfile.TemporaryFile('r+w+b')
    r = requests.get(loc, stream=True)
    for chunk in r.iter_content(chunk_size=4096):
        tmpf.write(chunk)
    tmpf.seek(0)
    sys.stdout.write("Done.\n")
    sys.stdout.flush()
    return tmpf


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u',
        '--url-to-list',
        default=DEFAULT_DOMAINS_LIST,
        help='URL to list of affected CloudFlare domains. '
             'Default is %s.' % DEFAULT_DOMAINS_LIST
    )
    parser.add_argument(
        '-o',
        '--output-file',
        type=argparse.FileType('wb'),
        help='File to output affected domains to as CSV'
    )
    parser.add_argument(
        '-f',
        '--fields',
        nargs='+',
        choices=['group', 'id', 'name', 'password', 'url', 'username'],
        default=['id', 'group', 'name', 'url', 'username'],
        help="Fields to use in output, defaults: 'id', 'group', 'name', "
             "'url', 'username'"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    domains_fobj = download_file(loc=args.url_to_list)
    make_dict(domains_fobj)
    domains_fobj.close()

    try:
        vault = get_vault()
    except Exception as e:
        print "Error while communicating with LastPass: %s" % e
        sys.exit(1)

    if args.output_file:
        print "Writing to file: %s" % os.path.abspath(args.output_file.name)
        domains_to_file(vault.accounts, args.output_file, args.fields)
    else:
        domains_to_stdout(vault.accounts)




if __name__ == '__main__':
    main()
