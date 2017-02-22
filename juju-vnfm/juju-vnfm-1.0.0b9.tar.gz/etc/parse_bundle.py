#!/usr/bin/env python

#
# Project:  juju-vnfm
# file:     parse_bundle
# created:  20/02/2017
#

"""
this file parse a bundle to a nsd.json
"""
import json
import logging
from optparse import OptionParser

import os.path
import yaml

__author__ = "lto"
__maintainer__ = "lto"

image_names = {
    'precise': 'precise-server-cloudimg-amd64-disk1',
    'trusty': 'trusty-server-cloudimg-amd64-disk1',
    'xenial': 'xenial-server-cloudimg-amd64-disk1',
}

if __name__ == '__main__':
    parser = OptionParser(usage='%prog [-d] source_file output_file', version='1')
    parser.add_option('-d', '--debug',
                      action='store_true', dest='debug', default=False,
                      help='enable debug mode')

    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error('input_file and output_file argument required')

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)

    if not os.path.isfile(args[0]):
        logging.error("File %s not existing" % args[0])

    bundle = None

    with open(args[0]) as input_file:
        bundle = yaml.load(input_file)

    result_nsd = {
        'version': bundle.get('series'),
        'vnfd': []
    }

    nsd_name = ""
    charms = bundle.get("services")
    # charmname
    for charm_name in charms:
        logging.info("Checking charm: %s" % charm_name)
        full_charm = charms.get(charm_name)
        vnfd = {}

        full_name = full_charm.get("charm").split("/")
        if len(full_name) >= 3:
            name = full_name[2]

            version = full_name[1]
        else:
            name = full_charm.get("charm").split("/")[1].split("-")[0]
            version = bundle.get("series")
        nsd_name += name + " "

        try:
            int(full_charm.get("charm").split("-")[len(full_charm.get("charm").split("-")) - 1])
            temp_type = full_charm.get("charm").split("-")[:len(full_charm.get("charm").split("-")) - 1]
        except:
            temp_type = full_charm.get("charm")

        type = "juju-charm-store/%s" % "".join(temp_type)

        options = full_charm.get("options")

        vnfd['name'] = name
        vnfd['version'] = version
        vnfd['type'] = type
        vnfd['vendor'] = 'fokus'
        vnfd['endpoint'] = 'juju'
        vnfd['configurations'] = {
            'name': "%s-config" % name,
            'configurationParameters': []
        }
        vnfd['deployment_flavour'] = []
        flavor = "m1.small"
        if full_charm.get('constaints'):
            constraints = full_charm.get('constaints').split(" ")
            for constraint in constraints:
                key, value = constraint.split("=")
                if key == "cpu-cores" and int(value) > 2:
                    flavor = "m1.medium"
                if key == "mem" and "2" in value:
                    flavor = "m1.small"
        vnfd['deployment_flavour'].append(
            {
                "flavour_key": flavor
            }
        )

        vnfd['lifecycle_event'] = [
            {
                "event": "CONFIGURE"
            }, {
                "event": "START"
            }
        ]
        if options is not None:
            for k, v in options.items():
                vnfd['configurations']['configurationParameters'].append(
                    {
                        'confKey': k,
                        'value': v
                    }
                )

        vnfd['configurations']['configurationParameters'].append(
            {
                'confKey': "SCRIPTS_PATH",
                'value': "/opt/openbaton/scripts"
            }
        )
        vnfd['vdu'] = []

        num_units = full_charm.get('num_units')
        if num_units is None:
            num_units = 1
        vnfd['vdu'].append({
            'name': "%s-1" % name,
            'scale_in_out': num_units,
            'vm_image': [image_names.get(bundle.get('series'))],
            'vnfc': []
        })
        for i in range(num_units):
            vnfd['vdu'][0]['vnfc'].append({'connection_point': [{
                "virtual_link_reference": "mgmt",
                "floatingIp": "random",
            }]})

        if not result_nsd.get('vnfd'):
            result_nsd['vnfd'] = []
        result_nsd['vnfd'].append(vnfd)

    """
    vnf_dependency:
    {
        "source":{
            "name":"bind9"
        },
        "target":{
            "name":"fhoss"
        },
        "parameters":[
            "useFloatingIpsForEntries",
            "realm",
            "mgmt",
            "mgmt_floatingIp"
        ]
    }
    """

    result_nsd['vnf_dependency'] = []
    for rel in bundle.get("relations"):
        target = rel[0]
        source = rel[1]
        result_nsd['vnf_dependency'].append(
            {
                'source': {
                    'name': source.split(":")[0]
                },
                'target': {
                    'name': target.split(":")[0]
                },
                'parameters': ["source_%s" % source.split(":")[1], "target_%s" % target.split(":")[1]]
            }
        )
    result_nsd['name'] = nsd_name + "NSD"
    with open(args[1], "w") as output_file:
        output_file.write(json.dumps(result_nsd, indent=2))
