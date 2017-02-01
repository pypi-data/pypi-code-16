# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .consistency_policy import ConsistencyPolicy
from .location import Location
from .failover_policy import FailoverPolicy
from .database_account import DatabaseAccount
from .failover_policies import FailoverPolicies
from .resource import Resource
from .database_account_create_update_parameters import DatabaseAccountCreateUpdateParameters
from .database_account_patch_parameters import DatabaseAccountPatchParameters
from .database_account_list_read_only_keys_result import DatabaseAccountListReadOnlyKeysResult
from .database_account_list_keys_result import DatabaseAccountListKeysResult
from .database_account_regenerate_key_parameters import DatabaseAccountRegenerateKeyParameters
from .database_account_paged import DatabaseAccountPaged
from .document_db_enums import (
    DatabaseAccountKind,
    DatabaseAccountOfferType,
    DefaultConsistencyLevel,
    KeyKind,
)

__all__ = [
    'ConsistencyPolicy',
    'Location',
    'FailoverPolicy',
    'DatabaseAccount',
    'FailoverPolicies',
    'Resource',
    'DatabaseAccountCreateUpdateParameters',
    'DatabaseAccountPatchParameters',
    'DatabaseAccountListReadOnlyKeysResult',
    'DatabaseAccountListKeysResult',
    'DatabaseAccountRegenerateKeyParameters',
    'DatabaseAccountPaged',
    'DatabaseAccountKind',
    'DatabaseAccountOfferType',
    'DefaultConsistencyLevel',
    'KeyKind',
]
