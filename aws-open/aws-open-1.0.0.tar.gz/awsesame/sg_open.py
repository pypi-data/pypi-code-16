#!/usr/bin/env python
# -*- coding: utf-8 -*-

from awsesame.utils import get_external_ip, get_sg_id_from_name
import boto3

def __open_one_sg(sg_name):
      sg_id = get_sg_id_from_name(sg_name)
      ec2 = boto3.resource('ec2')
      current_ip = get_external_ip()
      current_cidr = current_ip + "/32"
      security_group = ec2.SecurityGroup(sg_id)
      security_group.authorize_ingress(
                  IpProtocol='tcp',
                  FromPort=22,
                  ToPort=22,
                  CidrIp=current_cidr
                  )

def __open_all_sgs():
      ec2 = boto3.resource('ec2')
      print("Opening incoming port 22 on ALL Security Groups.")
      print("I hope you know what you're doing.")
      for sg in ec2.security_groups.all():
            print("Opening port 22 on SG %s" % sg.group_name)
            # security_group.authorize_ingress(
                        # IpProtocol='tcp',
                        # FromPort=22,
                        # ToPort=22,
                        # CidrIp=current_cidr
                        # )

def sg_open(sg_name=None, all_sgs=False):
      if all_sgs:
            __open_all_sgs()
      if sg_name is not None:
            __open_one_sg(sg_name)

