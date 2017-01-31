#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from flask import Flask, jsonify, redirect, url_for

from api2sshallowedusers import ssh
from api2sshallowedusers.helpers import *

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format=' '.join(['%(asctime)s | %(levelname)s |',
                                     '(%(name)s:%(funcName)s:%(lineno)d)',
                                     '%(message)s']))


def run_app(ssh_config, flask_config):
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    @authorize_badtoken
    def index():
        return jsonify(ssh_config.users)

    @app.route('/<user>', methods=['GET'])
    @authorize_badtoken
    @sanitize_user()
    def fakeuser(user):
        if user in ssh_config.users:
            return jsonify(True)
        else:
            return redirect(url_for('index'))

    @app.route('/<user>', methods=['ADD'])
    @authorize_badtoken
    @sanitize_user()
    def useradd(user):
        if ssh_config.add_user(user):
            ssh_config.sshd.reload()
            logger.info('Added user %s' % user)
            return jsonify({"OK": user + " added in " + ssh_config.filename})
        else:
            return abort(400)

    @app.route('/<user>', methods=['DEL'])
    @authorize_badtoken
    @sanitize_user()
    def userdel(user):
        if ssh_config.del_user(user):
            ssh_config.sshd.reload()
            return jsonify({"OK": ' '.join([user,
                                            "removed from",
                                            ssh_config.filename])})
        else:
            return abort(400)

    app.run(host=flask_config[0], port=flask_config[1])


def main(args=None):
    desc = " ".join(["list, add and remove allowed users from sshd_config",
                     "and reload daemon accordingly"])
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-l', '--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=5000)
    parser.add_argument('-f', '--file', default='/etc/ssh/sshd_config')
    parser.add_argument('-t', '--tokens', nargs='+', required=True)

    args = parser.parse_args()

    if os.getuid() != 0:
        logger.warning('Running as non-root. Is this ok ?')

    ssh_config = ssh.SSHConfig(args.file)
    TOKENS.extend(args.tokens)
    try:
        run_app(ssh_config, (args.host, args.port))
    except OSError as e:
        logger.error(e)
        sys.exit(1)
