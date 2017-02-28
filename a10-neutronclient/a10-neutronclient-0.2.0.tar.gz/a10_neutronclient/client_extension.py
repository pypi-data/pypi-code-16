# Copyright (C) 2016 A10 Networks Inc. All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import argparse

from neutronclient.common import extension
from neutronclient.neutron import v2_0 as neutronV20

_NEUTRON_OPTIONS = ['id', 'tenant_id']

JUST_NONE = object()


class ClientExtension(extension.NeutronClientExtension):

    def _arg_name(self, name, types, prefix="--"):
        if 'type:a10_nullable' in types:
            return self._arg_name(name, types['type:a10_nullable'], prefix)

        if 'type:a10_list' in types:
            return self._arg_name(name, types['type:a10_list'], prefix)

        if 'type:a10_reference' in types:
            if name.endswith('_id'):
                name = name[:-3]

        """--shish-kabob it"""
        return prefix + name.replace('_', '-')

    def _add_known_argument(self, parser, name, types):
        if 'type:a10_nullable' in types:
            parser.add_argument(
                self._arg_name(name, types, '--no-'),
                action='store_const',
                const=JUST_NONE,
                dest=name)

            self._add_known_argument(parser, name, types['type:a10_nullable'])
            return

        if 'type:a10_list' in types:
            parser.add_argument(
                self._arg_name(name, types['type:a10_list']),
                nargs='*',
                action='append',
                dest=name)
            return

        parser.add_argument(self._arg_name(name, types), dest=name)

    def _add_known_arguments(self, parser, required, ignore=[], where=lambda x: True):
        attributes = self.resource_attribute_map[self.resource_plural]
        for name in required:
            parser.add_argument(name)
        for name, attr in attributes.items():
            if name in required or name in _NEUTRON_OPTIONS or name in ignore or not where(attr):
                continue
            types = attr.get('validate', {})

            self._add_known_argument(parser, name, types)

    def alter_body(self, parsed_args, body):
        return body

    def _transform_arg(self, value, types):
        if value == JUST_NONE:
            return None

        if 'type:a10_nullable' in types:
            return self._transform_arg(value, types['type:a10_nullable'])

        if 'type:a10_list' in types:
            # argparse makes lists of lists
            # one sublist per instance of the argument
            return [self._transform_arg(x, types['type:a10_list'])
                    for sublist in value
                    for x in sublist]

        if 'type:a10_reference' in types:
            reference_to = types['type:a10_reference']
            return self.get_resource_id(reference_to, value)

        return value

    def args2body(self, parsed_args):
        attributes = self.resource_attribute_map[self.resource_plural]
        body = {}
        neutronV20.update_dict(parsed_args, body, [a for a in attributes if a != 'id'])

        for k in body:
            types = attributes.get(k, {}).get('validate', {})
            body[k] = self._transform_arg(body[k], types)

        altered = self.alter_body(parsed_args, body)
        return {self.resource: altered}

    def get_resource_id(self, resource, name_or_id):
        client = self.get_client()
        return neutronV20.find_resourceid_by_name_or_id(
            client,
            resource,
            name_or_id)


class List(extension.ClientExtensionList):
    pagination_support = True
    sorting_support = True


class Create(extension.ClientExtensionCreate):

    def _add_known_arguments(self, parser, required, ignore=[]):
        super(Create, self)._add_known_arguments(
            parser,
            required,
            ignore=ignore,
            where=lambda attr: attr.get('allow_post'))

    def add_known_arguments(self, parser):
        return self._add_known_arguments(parser, [])


class Update(extension.ClientExtensionUpdate):

    def _add_known_arguments(self, parser, required, ignore=[]):
        super(Update, self)._add_known_arguments(
            parser,
            required,
            ignore=ignore,
            where=lambda attr: attr.get('allow_put'))

    def add_known_arguments(self, parser):
        return self._add_known_arguments(parser, [])


class Delete(extension.ClientExtensionDelete):
    pass


class Show(extension.ClientExtensionShow):
    pass


class ReadFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        with open(values, 'r') as file:
            data = file.read()
            setattr(namespace, self.dest, data)
