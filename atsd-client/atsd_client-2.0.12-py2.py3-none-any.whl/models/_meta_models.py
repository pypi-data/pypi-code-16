# -*- coding: utf-8 -*-

"""
Copyright 2015 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""
from .._time_utilities import to_iso_utc

#------------------------------------------------------------------------------ 
class DataType(object):
    SHORT    = 'SHORT'
    INTEGER  = 'INTEGER'
    FLOAT    = 'FLOAT'
    LONG     = 'LONG'
    DOUBLE   = 'DOUBLE'

#------------------------------------------------------------------------------ 
class TimePrecision(object):
    SECONDS      = 'SECONDS'
    MILLISECONDS = 'MILLISECONDS'

#------------------------------------------------------------------------------ 
class InvalidAction(object):
    NONE      = 'NONE'
    DISCARD   = 'DISCARD'
    TRANSFORM = 'TRANSFORM'

#------------------------------------------------------------------------------ 
class Metric():
    """
    Class representing a single metric.
    Metrics are names assigned to numeric measurements, for example, temperature or speed.
    A time-indexed array of measurements for a given entity and metric is called a time-series (or simply series).
    Metrics specify how incoming data should be stored (data type), validated and pruned.
    In addition, metrics can have user-defined tags such as unit of measurement, scale, type or a category that can be used for filtering and grouping.
    """
    
    def __init__(self, 
                 name,
                 label=None,
                 enabled=None,
                 dataType=None,
                 timePrecision=None,
                 persistent=None,
                 filter=None,
                 minValue=None,
                 maxValue=None,
                 invalidAction=None,
                 description=None,
                 retentionInterval=None,
                 lastInsertDate=None,
                 tags=None,
                 versioned=None
                 ):
        #: `str` metric name
        self.name = name
        #: `str`
        self.label = label
        #: `bool`
        self.enabled = enabled
        #: :class:`.DataType`
        self.dataType = dataType
        #: :class:`.TimePrecision`
        self.timePrecision = timePrecision
        #: `bool` persistence status. Non-persistent metrics are not stored in the database and are only processed by the rule engine
        self.persistent = persistent
        #: If filter is specified, metric puts that do not match the filter are discarded
        self.filter = filter
        #: `Number` minimum value for Invalid Action trigger
        self.minValue = minValue
        #: `Number` maximum value for Invalid Action trigger
        self.maxValue = maxValue
        #: :class:`.InvalidAction`
        self.invalidAction = invalidAction
        #: `str` metric description
        self.description = description
        #: `Number` number of days to retain values for this metric in the database
        self.retentionInterval = retentionInterval
        #: :class:`datetime` object | `long` milliseconds | `str` ISO 8601 date. Last time a value was received for this metric by any series
        self.lastInsertDate = to_iso_utc(lastInsertDate)
        #: `dict`
        self.tags = tags
        #: `boolean` If set to true, enables versioning for the specified metric. When metrics is versioned, the database retains the history of series value changes for the same timestamp along with version_source and version_status 
        self.versioned = versioned

    def __repr__(self):
        return "<METRIC name={name}, label={label}, description={des}".format(name=self.name, label=self.label, des=self.description)
    
    #Getters and setters
    def get_name(self):
        return self.name

    def get_label(self):
        return self.label

    def get_enabled(self):
        return self.enabled

    def get_data_type(self):
        return self.dataType

    def get_time_precision(self):
        return self.timePrecision

    def get_persistent(self):
        return self.persistent

    def get_filter(self):
        return self.filter

    def get_min_value(self):
        return self.minValue

    def get_max_value(self):
        return self.maxValue

    def get_invalid_action(self):
        return self.invalidAction

    def get_description(self):
        return self.description

    def get_retention_interval(self):
        return self.retentionInterval

    def get_last_insert_date(self):
        return self.lastInsertDate

    def get_tags(self):
        return self.tags

    def get_versioned(self):
        return self.versioned

    def set_name(self, value):
        self.name = value

    def set_label(self, value):
        self.label = value

    def set_enabled(self, value):
        self.enabled = value

    def set_data_type(self, value):
        self.dataType = value

    def set_time_precision(self, value):
        self.timePrecision = value

    def set_persistent(self, value):
        self.persistent = value

    def set_filter(self, value):
        self.filter = value

    def set_min_value(self, value):
        self.minValue = value

    def set_max_value(self, value):
        self.maxValue = value

    def set_invalid_action(self, value):
        self.invalidAction = value

    def set_description(self, value):
        self.description = value

    def set_retention_interval(self, value):
        self.retentionInterval = value

    def set_last_insert_date(self, value):
        self.lastInsertDate = to_iso_utc(value)

    def set_tags(self, value):
        self.tags = value

    def set_versioned(self, value):
        self.versioned = value
    
#------------------------------------------------------------------------------ 
class Entity():
    """
    Class representing a single entitiy.
    Entities are servers, hosts, frames, virtual machines, sensors, etc.
    Entities are ingested with attached metrics (time series data) using the csv/nmon parsers, telnet and http/s protocols, and Axibase Collector jobs.
    """
    
    def __init__(self, name, enabled=None, lastInsertDate=None, tags=None):
        # `str` entity name
        self.name = name
        #: `bool` enabled status. Incoming data is discarded for disabled entities
        self.enabled = enabled
        #: :class:`datetime` object | `long` milliseconds | `str` ISO 8601 date. Last time when a value was received by the database for this entity
        self.lastInsertDate = to_iso_utc(lastInsertDate)
        #: `dict`
        self.tags = tags
        
    def __repr__(self):
        return "<Entity name={name}, enabled={enabled}, lastInsertDate={lit}, tags={tags}".format(name=self.name, enabled=self.enabled, lit=self.lastInsertDate, tags=self.tags)

    #Getters and setters
    def get_name(self):
        return self.name

    def get_enabled(self):
        return self.enabled

    def get_last_insert_date(self):
        return self.lastInsertDate

    def get_tags(self):
        return self.tags

    def set_name(self, value):
        self.name = value

    def set_enabled(self, value):
        self.enabled = value

    def set_last_insert_date(self, value):
        self.lastInsertDate = to_iso_utc(value)

    def set_tags(self, value):
        self.tags = value

#------------------------------------------------------------------------------ 
class EntityGroup():
    """
    Class representing a single entity group.
    Entities can be grouped into Entity Groups which can be used for building Portals, Exporting Data, and creating Forecasts.
    Forecasts can be calculated for all entities present in the group.
    Data or Forecasts can be exported for all entities present in the group.
    Portals can be added to all entities present in the Group.
    This is a useful feature when working with large amounts of entities and big data sets.
    """
    def __init__(self, name, expression=None, tags=None):
        #: `str` entity group name
        self.name = name
        #: `str` group membership expression. The expression is applied to entities to automatically add/remove members of this group
        self.expression = expression
        #: `dict`
        self.tags = tags
    
    def __repr__(self):
        return "<EntityGroup name={name}, expression={expression}, tags={tags}".format(name=self.name, expression=self.expression, tags=self.tags)
    
    #Getters and setters
    def get_name(self):
        return self.name

    def get_expression(self):
        return self.expression

    def get_tags(self):
        return self.tags

    def set_name(self, value):
        self.name = value

    def set_expression(self, value):
        self.expression = value

    def set_tags(self, value):
        self.tags = value
