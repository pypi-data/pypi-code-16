#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
from ipaddress import IPv4Network, IPv4Address
from .utils import get_external_ip

def list_open_sgs():
      ec2 = boto3.resource('ec2')
      current_ip = IPv4Address(get_external_ip())
      open_sgs = []
      for sg in ec2.security_groups.all():
            perms = get_open_permissions(sg, current_ip)
            if perms:
                  open_sgs.append((sg, perms))

      return open_sgs

def list_closed_sgs():
      ec2 = boto3.resource('ec2')
      current_ip = IPv4Address(get_external_ip())
      closed_sgs = []
      for sg in ec2.security_groups.all():
           if not get_open_permissions(sg, current_ip):
                  closed_sgs.append(sg)

      return closed_sgs


def print_open_sgs():
      tuples = list_open_sgs()
      for sg, permissions in tuples:
            print("%s open due to permissions:" % sg.group_name)
            for permission in permissions:
                  print(permission)

def print_closed_sgs():
      sgs = list_closed_sgs()
      for sg in sgs:
            print (sg.group_name)

def get_open_permissions(security_group, ip_address):
      permissions = []
      for permission in security_group.ip_permissions:
            if permission.get('IpProtocol') == 'tcp' and \
               22 in range(permission.get('FromPort'), permission.get('ToPort') + 1):
                     for ip_range in permission.get('IpRanges'):
                           network = IPv4Network(ip_range.get('CidrIp'))
                           if ip_address in network:
                                 permissions.append(permission)
      return permissions
