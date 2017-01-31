# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
#pylint: skip-file

# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator 0.17.0.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from enum import Enum


class monitorProtocol(Enum):

    http = "http"
    https = "https"


class routingMethod(Enum):

    priority = "priority"
    performance = "performance"
    weighted = "weighted"


class status(Enum):

    enabled = "enabled"
    disabled = "disabled"


class DeploymentMode(Enum):

    incremental = "Incremental"
    complete = "Complete"
