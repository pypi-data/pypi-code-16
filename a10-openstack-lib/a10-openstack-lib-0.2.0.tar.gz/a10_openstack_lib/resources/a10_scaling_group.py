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

EXTENSION = 'a10-scaling-group'

SERVICE = "A10_SCALING_GROUP"

SCALING_GROUPS = 'a10_scaling_groups'
SCALING_GROUP = 'a10_scaling_group'

SCALING_GROUP_WORKERS = 'a10_scaling_group_workers'
SCALING_GROUP_WORKER = 'a10_scaling_group_worker'

SCALING_POLICIES = 'a10_scaling_policies'
SCALING_POLICY = 'a10_scaling_policy'

SCALING_ALARMS = 'a10_scaling_alarms'
SCALING_ALARM = 'a10_scaling_alarm'

SCALING_ACTIONS = 'a10_scaling_actions'
SCALING_ACTION = 'a10_scaling_action'

ALARM_UNITS = ['count', 'percentage', 'bytes']
ALARM_AGGREGATIONS = ['avg', 'min', 'max', 'sum']
ALARM_MEASUREMENTS = ['connections', 'memory', 'cpu', 'interface']
ALARM_OPERATORS = ['>=', '>', '<=', '<']
ALARM_PERIOD_UNITS = ['minute', 'hour', 'day']
ACTIONS = ['scale-in', 'scale-out']

RESOURCE_ATTRIBUTE_MAP = {
    SCALING_GROUPS: {
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
        'scaling_policy_id': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:a10_nullable': {
                    'type:uuid': None,
                    'type:a10_reference': SCALING_POLICY
                }
            },
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        }
    },
    SCALING_GROUP_WORKERS: {
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
        'scaling_group_id': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:uuid': None,
                'type:a10_reference': SCALING_GROUP
            },
            'is_visible': True
        },
        'host': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:string': None
            },
            'is_visible': True
        },
        'username': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:string': None
            },
            'is_visible': True
        },
        'password': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:string': None
            },
            'is_visible': False
        },
        'api_version': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:values': ['2.1', '3.0']
            },
            'is_visible': True
        },
        'protocol': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:values': ['http', 'https']
            },
            'convert_to': lambda attr: validators.convert_to_lower,
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        },
        'port': {
            'allow_post': False,
            'allow_put': True,
            'validate': {
                'type:range': [0, 65535]
            },
            'convert_to': lambda attr: attr.convert_to_int,
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        },
        'nova_instance_id': {
            'allow_post': False,
            'allow_put': False,
            'validate': {
                'type:uuid': None
            },
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        },
        'nova_flavor': {
            'allow_post': True,
            'allow_put': False,
            'validate': {
                'type:string': None
            },
            'is_visible': False,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        }
    },
    SCALING_POLICIES: {
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
        'cooldown': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:non_negative': None
            },
            'convert_to': lambda attr: attr.convert_to_int,
            'is_visible': True,
            'default': 300,
        },
        'min_instances': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:non_negative': None
            },
            'convert_to': lambda attr: attr.convert_to_int,
            'is_visible': True,
            'default': 1,
        },
        'max_instances': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:a10_nullable': {
                    'type:non_negative': None
                }
            },
            'convert_to': lambda attr: validators.convert_nullable(attr.convert_to_int),
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        },
        'reactions': {
            'allow_post': True,
            'allow_put': True,
            'convert_list_to': lambda attr: attr.convert_kvp_list_to_dict,
            'is_visible': True,
            'default': lambda attr: attr.ATTR_NOT_SPECIFIED
        }
    },
    SCALING_ALARMS: {
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
        'aggregation': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['avg', 'min', 'max', 'sum']
            },
            'is_visible': True,
            'convert_to': lambda attr: validators.convert_to_lower,
            'default': 'avg'
        },
        'measurement': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['connections', 'memory', 'cpu', 'interface']
            },
            'convert_to': lambda attr: validators.convert_to_lower,
            'is_visible': True
        },
        'operator': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['>=', '>', '<=', '<']
            },
            'is_visible': True
        },
        'threshold': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:a10_float': None
            },
            'convert_to': lambda attr: validators.convert_to_float,
            'is_visible': True
        },
        'unit': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['count', 'percentage', 'bytes']
            },
            'convert_to': lambda attr: validators.convert_to_lower,
            'is_visible': True
        },
        'period': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:non_negative': None
            },
            'convert_to': lambda attr: attr.convert_to_int,
            'is_visible': True,
        },
        'period_unit': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['minute', 'hour', 'day']
            },
            'convert_to': lambda attr: validators.convert_to_lower,
            'is_visible': True
        }
    },
    SCALING_ACTIONS: {
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
        'action': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:values': ['scale-in', 'scale-out']
            },
            'convert_to': lambda attr: validators.convert_to_lower,
            'is_visible': True
        },
        'amount': {
            'allow_post': True,
            'allow_put': True,
            'validate': {
                'type:non_negative': None
            },
            'convert_to': lambda attr: attr.convert_to_int,
            'is_visible': True,
        },
    }
}

VALIDATORS = validators.VALIDATORS
