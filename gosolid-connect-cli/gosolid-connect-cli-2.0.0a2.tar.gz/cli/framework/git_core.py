import os
import sys
import cli.configuration
import requests
import json
import pprint
from git import Repo


class Git():
    def __init__(self, property_data, user_data, directory):
        self.user_data = user_data
        self.property_data = property_data
        self.url = cli.configuration.BASE_URL
        self.repository_url = self.url + 'property/%s/vc/repository' %(self.property_data['id'])
        self.repository_data = self.get_repository_data()
        if directory is not None:
            self.repo_dest = os.path.join(os.getcwd() + '/%s' % directory)
        else:
            self.repo_dest = os.path.join(os.getcwd() + '/%s' % self.property_data['code'].lower())

    def get_repository_data(self):
        r = requests.get(self.repository_url, headers={
            'email': self.user_data['email'],
            'secret-key': self.user_data['secret_key']
        })
        parsed_reply = json.loads(r.text)
        return parsed_reply['result']

    def init_repo(self):
        username = self.user_data['bitbucket_username']
        password = self.user_data['bitbucket_password']
        repository = self.repository_data['url']
        url = cli.configuration.BITBUCKET_URL % {
            'username': username,
            'password': password,
            'repository': repository
        }
        if self.repository_data['id']:
            try:
                Repo.clone_from(url, self.repo_dest, branch=cli.configuration.DEFAULT_GIT_BRANCH, progress=False)
                print('Successfully initialized repo for %s in %s.' %(repository, self.repo_dest))
            except:
                print('Failed to initialize Git repository. Exiting.')
                sys.exit()
        else:
            print("FATAL: Repository not found. Exiting.")