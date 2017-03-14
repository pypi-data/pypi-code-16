# Copyright 2016 Formation Data Systems, Inc. All Rights Reserved.
#

from test.base_cli_test import BaseCliTest
from mock import patch
import collections
import mock_functions
from fdscli.model.fds_error import FdsError
from fdscli.functions.datetime_functions import DatetimeFunctions

class DatetimeTests(BaseCliTest):
    '''Tests for computing datetime ranges.
    '''

    def test_bad_begin_date(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2016-06-02-42" # Not YYYY-MM-DD

        exception = None

        try:
            result = util.validate_timestamp_filter(d)
        except Exception as ex:
            exception = ex

        assert exception is None
        assert isinstance(result, FdsError) is True

    def test_bad_begin_time(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2016-06-02"
        d["begin_time"] = "25:60" # Invalid time for HH:MM

        exception = None

        try:
            result = util.validate_timestamp_filter(d)
        except Exception as ex:
            exception = ex

        assert exception is None
        assert isinstance(result, FdsError) is True

    def test_bad_end_date(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2016-01-01"
        d["end_date"] = "2016-06-02-42" # Not YYYY-MM-DD

        exception = None

        try:
            result = util.validate_timestamp_filter(d)
        except Exception as ex:
            exception = ex

        assert exception is None
        assert isinstance(result, FdsError) is True

    def test_bad_end_time(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2016-01-01"
        d["end_date"] = "2016-06-02"
        d["end_time"] = "25:60" # Invalid time for HH:MM

        exception = None

        try:
            result = util.validate_timestamp_filter(d)
        except Exception as ex:
            exception = ex

        assert exception is None
        assert isinstance(result, FdsError) is True

    def test_begin_range(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2016-06-02"

        result = util.validate_timestamp_filter(d)

        assert isinstance(result, collections.Iterable) is True
        assert len(result) == 2
        assert result[0] == 1464825600 # GMT

        d["begin_time"] = "01:00" # 3600 seconds

        result2 = util.validate_timestamp_filter(d)

        assert isinstance(result2, collections.Iterable) is True
        assert len(result2) == 2
        assert (result2[0] - result[0]) == 3600

    def test_empty_range(self):

        util = DatetimeFunctions()

        d = dict()
        result = util.validate_timestamp_filter(d)

        assert isinstance(result, collections.Iterable) is True
        assert len(result) == 0

    def test_end_range(self):

        util = DatetimeFunctions()

        d = dict()
        d["begin_date"] = "2015-01-01"
        d["end_date"] = "2016-06-02"

        result = util.validate_timestamp_filter(d)

        assert isinstance(result, collections.Iterable) is True
        assert len(result) == 2
        assert result[1] == 1464825600 # GMT

        d["end_time"] = "01:00" # 3600 seconds

        result2 = util.validate_timestamp_filter(d)

        assert isinstance(result2, collections.Iterable) is True
        assert len(result2) == 2
        assert (result2[1] - result[1]) == 3600

