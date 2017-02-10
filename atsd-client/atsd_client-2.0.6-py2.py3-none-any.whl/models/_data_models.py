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

import copy
from .._constants import display_series_threshold, display_series_part
from .._time_utilities import to_timestamp, to_iso_utc

#------------------------------------------------------------------------------ 
class Sample():
    """
    Class that represents a numeric value observed at some time with additional version information if provided.
    If multiple samples have the same timestamp and are inserted for the same series, the latest sample prevails, unless the metric is optionally enabled for version tracking.
    """
    
    def __init__(self, value, time=None, version=None):
        self.v = copy.deepcopy(value) if not value == "Nan" else float("nan")
        #:class:`datetime` object | `long` milliseconds | `str`  ISO 8601 date 
        self.t = to_timestamp(time)
        #`.dict` version object including 'source' and 'status' keys
        self.version = version

    def __repr__(self):
        return "<Sample v={v}, t={t}, version={vv}>".format(v=self.v, t=self.t, vv=self.version)
    
    #Getters and setters
    def get_v(self):
        return self.v

    def get_t(self):
        return self.t

    def set_v(self, v):
        self.v = v

    def set_t(self, t):
        self.t = to_timestamp(t)
        
    def get_version(self):
        return self.version

    def set_version(self, value):
        self.version = value

        
    def _compare(self, other):
            return self.t - other.get_t()

    def __lt__(self, other):
        return self._compare(other) < 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __eq__(self, other):
        return self._compare(other) == 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __ne__(self, other):
        return self._compare(other) != 0
  
#------------------------------------------------------------------------------ 
class Series():
    """
    Class representing a Time Series.
    Time Series is a time-indexed array of samples (observations), each consisting of a timestamp and a numeric value, for example CPU utilization or body temperature.
    Each series is uniquely identified by entity name, metric name and optional series tags.
    """
    
    def __init__(self, entity, metric, data=None, tags=None):
        #: `str` entity name
        self.entity = entity
        #: `str` metric name
        self.metric = metric
        #: `dict` of ``tag_name: tag_value`` pairs
        self.tags = tags
        # `list` of :class:`.Sample` objects| `list` of {'t': time, 'v': value} objects
        self.data = []
        if data is not None:
            for data_unit in data:
                if isinstance(data_unit, dict): #Compatability
                    self.data.append(Sample(
                                            value=data_unit['v'],
                                            time=data_unit.get('t', data_unit.get('d', None)), 
                                            version=data_unit.get('version', None)
                                            )
                                    )
                else:
                    self.data.append(data_unit)
    
    def __repr__(self):
        if len(self.data) > display_series_threshold:
            displayed_data = self.data[:display_series_part] + self.data[-display_series_part:]
        else:
            displayed_data = self.data
        rows = []
        versioned = False
        for sample in sorted(displayed_data):
            time = sample.t
            value = sample.v
            row = '{0}{1: >14}'.format(time, value)
            if sample.version is not None:
                versioned = True
                source = sample.version.get('source', '-')
                status = sample.version.get('status', '-')
                row += '{0: >17}{1: >17}'.format(source, status)
            rows.append(row)
        if versioned:
            header = ('           time'
                      '         value'
                      '   version_source'
                      '   version_status'
                      )
            rows.insert(0, header)
        if len(self.data) > 20:
            result = '\n'.join(rows[:-display_series_part]) + '\n...\n' + '\n'.join(rows[-display_series_part:])
        else:
            result = '\n'.join(rows)
        for attr_name in self.__dict__:
            if not attr_name.startswith('_'):
                result += '\n{0}: {1}'.format(attr_name, getattr(self, attr_name))
        return result

    def add_samples(self, *samples):
        """
        Add all given samples to series
        """
        for sample in samples:
            self.data.append(sample)
        
    def sort(self, key=None, reverse=False):
        """
        Sort series data in place
        :param key:
        :param reverse:
        """
        self.data.sort(key=key, reverse=reverse)
    
    def values(self):
        """
        Valid versions of series values
        :return: list of `Number`
        """
        data = sorted(self.data)
        result = []
        for num, sample in enumerate(data):
            if num > 0 and sample.t == data[num - 1].t:
                result.pop()
            result.append(sample.v)
        return result

    def times(self):
        """
        Valid versions of series times in seconds
        :return: list of `float`
        """
        data = sorted(self.data)
        result = []
        for num, sample in enumerate(data):
            if num > 0 and sample.t == data[num - 1].t:
                result.pop()
            new_time = to_iso_utc(sample.t)
            result.append(new_time)
        return result

    @staticmethod
    def from_pandas_series(entity, metric, ts):
        """
        :param entity: `str` entity name
        :param metric: `str` metric name
        :param ts: pandas time series object
        :return: :class:`.Series` with data from pandas time series
        """
        res = Series(entity, metric)
        for dt in ts.index:
            res.add_sample(ts[dt], dt)
        return res

    def to_pandas_series(self):
        """
        :return: pandas time series object
        """
        import pandas as pd
        return pd.Series(self.values(), index=self.times())

    def plot(self):
        """
        Plot series in matplotlib.pyplot
        """
        try:
            return self.to_pandas_series().plot()
        except ImportError:
            import matplotlib.pyplot as plt
            p = plt.plot(self.times(), self.values())
            plt.show(p)
            
    #Getters and setters       
    def get_entity(self):
        return self.entity

    def get_metric(self):
        return self.metric

    def get_tags(self):
        return self.tags

    def get_data(self):
        return self.data

    def set_entity(self, value):
        self.entity = value

    def set_metric(self, value):
        self.metric = value

    def set_tags(self, value):
        self.tags = value

    def set_data(self, value):
        self.data = value

#------------------------------------------------------------------------------ 
class Property():
    """
    Class representing a single property.
    Properties represent metadata describing entities, obtained from configuration files, system command output, etc.
    Property examples are device model, OS version, and location. Unlike time series, the database stores only last value for each property and such value is stored as text. 
    Properties are collected at a lower frequency than time series or whenever their values change. 
    Each properties record is uniquely identified by entity name, property type and optional property keys.
    """
        
    def __init__(self, type, entity, tags=None, key=None, date=None):
        #: `str` property type name
        self.type = type
        #: `str` entity name
        self.entity = entity
         #: `dict` of ``name: value`` pairs that are not part of the key and contain descriptive information about the property record.
        self.tags = tags
        #: `dict` of ``name: value`` pairs that uniquely identify the property record
        self.key = key
        #: :class:`datetime` object | `long` milliseconds | `str`  ISO 8601 date, for example 2016-05-25T00:15:00Z. Set to server time at server side if omitted.
        self.date = to_iso_utc(date)

    def __repr__(self):
            return "<PROPERTY type={type}, entity={entity}, tags={tags}...>".format(type=self.type, entity=self.entity, tags=self.tags)
    
    
    #Getters and setters    
    def get_type(self):
        return self.type

    def get_entity(self):
        return self.entity

    def get_tags(self):
        return self.tags

    def get_key(self):
        return self.key

    def get_date(self):
        return self.date

    def set_type(self, value):
        self.type = value

    def set_entity(self, value):
        self.entity = value

    def set_tags(self, value):
        self.tags = value

    def set_key(self, value):
        self.key = value

    def set_date(self, value):
        self.date = to_iso_utc(value)
       
#------------------------------------------------------------------------------ 
class Alert():
    """
    Class, representing an single alert.
    Alert is an event produced by the rule engine by applying pre-defined rules to incoming data. 
    An alert is created when an expression specified in the rule evaluates to true and it is closed, when the expression returns false.
    The users can set acknowledge/de-acknowledge status for open alerts.
    The rule expressions can operate on series, message, and property commands.
    """

    def __init__(self, id, rule=None, entity=None, metric=None, lastEventDate=None, openDate=None, value=None, message=None, tags=None, textValue=None, severity=None, repeatCount=None, acknowledged=None, openValue=None):
        self.id = id
        #: `str` rule
        self.rule = rule
        #: `str` entity
        self.entity = entity
        #: `str` metric
        self.metric = metric
        #: `str` | :class:`datetime` | `long` milliseconds when the last record was received
        self.lastEventDate = to_iso_utc(lastEventDate)
        #: `str` | :class:`datetime` | `long` milliseconds when the alert was open
        self.openDate = to_iso_utc(openDate)
        #: `Number` last numeric value received
        self.value = value
        #: `dict`
        self.tags = tags
        #: `str` text value
        self.textValue = textValue
        #: :class:`.Severity`
        self.severity = severity
        #: `int` number of times when the expression evaluated to true sequentially
        self.repeatCount = repeatCount
        #: `bool` acknowledgement status
        self.acknowledged = acknowledged
        #: `Number` first numeric value received.
        self.openValue = openValue

    def __repr__(self):
            return "<ALERT id={id}, text={text}, entity={entity}, metric={metric}, openDate={openDate}...>".format(id=self.id, entity=self.entity, metric=self.metric, openDate=self.openDate, text=self.textValue)
            
    #Getters and setters
    def get_id(self):
        return self.id

    def get_entity(self):
        return self.entity

    def get_metric(self):
        return self.metric

    def get_open_date(self):
        return self.openDate

    def get_text_value(self):
        return self.textValue

    def get_rule(self):
        return self.rule

    def get_last_event_date(self):
        return self.lastEventDate

    def get_value(self):
        return self.value

    def get_message(self):
        return self.message

    def get_tags(self):
        return self.tags

    def get_severity(self):
        return self.severity

    def get_repeat_count(self):
        return self.repeatCount

    def get_acknowledged(self):
        return self.acknowledged

    def get_open_value(self):
        return self.openValue

    def set_id(self, value):
        self.id = value

    def set_entity(self, value):
        self.entity = value

    def set_metric(self, value):
        self.metric = value

    def set_open_date(self, value):
        self.openDate = to_iso_utc(value)

    def set_text_value(self, value):
        self.textValue = value

    def set_rule(self, value):
        self.rule = value

    def set_last_event_date(self, value):
        self.lastEventDate = to_iso_utc(value)

    def set_value(self, value):
        self.value = value

    def set_message(self, value):
        self.message = value

    def set_tags(self, value):
        self.tags = value

    def set_severity(self, value):
        self.severity = value

    def set_repeat_count(self, value):
        self.repeatCount = value

    def set_acknowledged(self, value):
        self.acknowledged = value

    def set_open_value(self, value):
        self.openValue = value

#------------------------------------------------------------------------------ 
class AlertHistory():
    """
    Class representing history of an alert, including such values as alert duration, alert open date, repeat count, etc.
    """
  
    def __init__(self, alert=None, alertDuration=None, alertOpenDate=None, entity=None, metric=None, receivedDate=None, repeatCount=None, rule=None, ruleExpression=None, ruleFilter=None, severity=None, tags=None, type=None, date=None, value=None, window=None):
        self.alert = alert
        #: `Number` time in milliseconds when alert was in OPEN or REPEAT state
        self.alertDuration = alertDuration
        #: `str` | :class:`datetime` | `long`    
        self.alertOpenDate = to_iso_utc(alertOpenDate)
        #: `str`
        self.entity = entity
        #: `str`
        self.metric = metric
        #: `str` | :class:`datetime` | `long` 
        self.receivedDate = to_iso_utc(receivedDate)
        #: `int`
        self.repeatCount = repeatCount
        #: `str`
        self.rule = rule
        #: `str`
        self.ruleExpression = ruleExpression
        #: `str`
        self.ruleFilter = ruleFilter
        #: :class:`.Severity`
        self.severity = severity
        #: `str`
        self.tags = tags
        #: `str` alert state when closed: OPEN, CANCEL, REPEAT
        self.type = type
        #: :class:`datetime` object | `long` milliseconds | `str` ISO 8601 date
        self.date = to_iso_utc(date)
        #: `Number` last numeric value received
        self.value = value
        #: `int` window length
        self.window = window

    def __repr__(self):
            return "<ALERT_HISTORY alert={alert}, metric={metric}, entity={entity}, date={date}, alertOpenDate={alertOpenDate}...>".format(alert=self.alert, entity=self.entity, metric=self.metric, alertOpenDate=self.alertOpenDate, date=self.date)
    
    #Getters and setters
    def get_alert(self):
        return self.alert

    def get_entity(self):
        return self.entity

    def get_metric(self):
        return self.metric

    def get_alert_open_date(self):
        return self.alertOpenDate

    def get_date(self):
        return self.date

    def get_alert_duration(self):
        return self.alertDuration

    def get_received_date(self):
        return self.receivedDate

    def get_repeat_count(self):
        return self.repeatCount

    def get_rule(self):
        return self.rule

    def get_rule_expression(self):
        return self.ruleExpression

    def get_rule_filter(self):
        return self.ruleFilter

    def get_schedule(self):
        return self.schedule

    def get_severity(self):
        return self.severity

    def get_tags(self):
        return self.tags

    def get_type(self):
        return self.type

    def get_value(self):
        return self.value

    def get_window(self):
        return self.window

    def set_alert(self, value):
        self.alert = value

    def set_entity(self, value):
        self.entity = value

    def set_metric(self, value):
        self.metric = value

    def set_alert_open_date(self, value):
        self.alertOpenDate = to_iso_utc(value)

    def set_date(self, value):
        self.date = to_iso_utc(value)

    def set_alert_duration(self, value):
        self.alertDuration = value

    def set_received_date(self, value):
        self.receivedDate = to_iso_utc(value)

    def set_repeat_count(self, value):
        self.repeatCount = value

    def set_rule(self, value):
        self.rule = value

    def set_rule_expression(self, value):
        self.ruleExpression = value

    def set_rule_filter(self, value):
        self.ruleFilter = value

    def set_schedule(self, value):
        self.schedule = value

    def set_severity(self, value):
        self.severity = value

    def set_tags(self, value):
        self.tags = value

    def set_type(self, value):
        self.type = value

    def set_value(self, value):
        self.value = value

    def set_window(self, value):
        self.window = value

#------------------------------------------------------------------------------ 
class Message():
    """
    Class representing a Message.
    Messages are events collected from system logs and messaging systems.
    Messages are stored in ATSD to support correlation with other data types, for example, to relate log events with resource bottleneck alerts.
    Each message is related to an entity, has a set of tags and a free-form text message.
    Messages for the same entity, time and type/source tags are automatically de-duplicated.
    """
  
    def __init__(self, type, source, entity, date, severity, tags, message):
        #: `str` message type
        self.type = type
        #: `str` message source
        self.source = source
        #: `str` entity name
        self.entity = entity
        #:`datetime` | `long` milliseconds | `str` ISO 8601 date when the message record was created 
        self.date = to_iso_utc(date)
        #: :class:`.Severity`
        self.severity = severity
        #: `str` message tags
        self.tags=tags
        #: `str`
        self.message=message
    
    def __repr__(self):
        return "<MESSAGE type={t}, source={s}, entity={e}, message={m}, date={d}...>".format(t=self.type, s=self.source, e=self.entity, m=self.message, d=self.date)
    
    #Getters and setters
    def get_type(self):
        return self.type

    def get_entity(self):
        return self.entity

    def get_source(self):
        return self.source

    def get_date(self):
        return self.date

    def get_severity(self):
        return self.severity

    def get_tags(self):
        return self.tags

    def get_message(self):
        return self.message

    def set_type(self, value):
        self.type = value

    def set_entity(self, value):
        self.entity = value

    def set_source(self, value):
        self.source = value

    def set_date(self, value):
        self.date = to_iso_utc(value)

    def set_severity(self, value):
        self.severity = value

    def set_tags(self, value):
        self.tags = value

    def set_message(self, value):
        self.message = value
