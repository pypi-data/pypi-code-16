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

import validators

EXTENSION = 'a10-certificate'

SERVICE = "A10_CERTIFICATE"

CERTIFICATES = 'a10_certificates'
CERTIFICATE = 'a10_certificate'

CERTIFICATE_BINDING = 'a10_certificate_binding'
CERTIFICATE_BINDINGS = 'a10_certificate_bindings'

RESOURCE_ATTRIBUTE_MAP = {
    CERTIFICATES: {
        'id': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:uuid': None
            },
            'is_visible': True,
            'primary_key': True
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'required_by_policy': True,
            'is_visible': True
        },
        'name': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:string': None
            },
            'is_visible': True,
            'default': ''
        },
        'description': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:string': None
            },
            'is_visible': True,
            'default': '',
        },
        'cert_data': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:string': None
            },
            'is_visible': False,
        },
        'key_data': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:string': None
            },
            'is_visible': False,
        },
        'intermediate_data': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:string': None,
            },
            'is_visible': False,
            'default': ''
        },
        'password': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:string': None,
            },
            'is_visible': False,
            'default': ''

        }
    },

    CERTIFICATE_BINDINGS: {
        'id': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True,
            'primary_key': True,
            'validate': {
                'type:uuid': None
            }
        },
        'tenant_id': {
            'allow_post': True,
            'allow_put': False,
            'required_by_policy': True,
            'is_visible': True
        },
        'certificate_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'validate': {
                'type:uuid': None,
                'type:a10_reference': CERTIFICATE,
            },
        },
        'listener_id': {
            'allow_post': True,
            'allow_put': True,
            'is_visible': True,
            'validate': {
                'type:uuid': None,
                'type:a10_reference': "listener",
            },
        },
        'listener_name': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True
        },
        'certificate_name': {
            'allow_post': False,
            'allow_put': False,
            'is_visible': True
        }
    }
}

VALIDATORS = validators.VALIDATORS
