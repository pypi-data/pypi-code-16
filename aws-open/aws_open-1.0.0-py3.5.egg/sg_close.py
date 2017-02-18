#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .utils import get_external_ip, get_sg_id_from_name, get_all_sgs
from ipaddress import IPv4Address
from .sg_list import get_open_permissions
import boto3

def sg_close(sg_name=None, all_sgs=False):
      if all_sgs:
            sgs = get_all_sgs()
      else:
            ec2 = boto3.resource('ec2')
            sg_id = get_sg_id_from_name(sg_name)
            sgs = [ec2.SecurityGroup(sg_id)]
      
      current_ip = IPv4Address(get_external_ip())
      for security_group in sgs:
            permissions = get_open_permissions(security_group, current_ip)
            if permissions:
                  print('Closing SSH to this IP on Security Group %s via permissions:' % security_group.group_name)
                  security_group.revoke_ingress(IpPermissions=permissions)
                  for permission in permissions:
                        print(permission)
