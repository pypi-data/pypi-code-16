# coding=utf8

import click
import subprocess

from family.deploy.aliyun import Listener

import ConfigParser, os

config = ConfigParser.ConfigParser()


@click.command()
@click.option('--slb', '-s', help='SLB id')
@click.option('--port', '-p', default='3000', help='port')
@click.option('--conf', '-c', help='configure')
def init_listener(slb, port, conf):
    config.readfp(open(conf))
    access_id = config.get('aliyun', 'access_id')
    access_secret = config.get('aliyun', 'access_secret')
    region = config.get('aliyun', 'region')
    listener = Listener(access_id, access_secret, region)
    listener.add_listener(slb, port)
    listener.start_listener(slb, port)
