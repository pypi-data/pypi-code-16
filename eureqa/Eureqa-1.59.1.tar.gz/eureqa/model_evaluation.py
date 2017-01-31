# Copyright (c) 2017, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from error_metric import ErrorMetrics

class ModelEvaluation(object):
    """ Represents the result of evaluting solutions and expressions.

    :var dict data: The dictionary, where keys are expressions and variable names, and values are columns of data.
    :var pandas.PandFrame frame: The Pandas frame, where column names are expressions and variable names.
    :var list error_metrics: The list of :py:class:`~eureqa.error_metric.ErrorMetrics` for provided solutions.

    """

    def __init__(self, body):
        """For internal use only
        PARAM_NOT_EXTERNALLY_DOCUMENTED
        """
        self._body = body
        self._columns = body.get('columns')
        self._csv_data = body.get('csv_data')
        self._datetime_column = body.get('datetime_column')
        self._series_id_column = body.get('series_id_column')
        if 'error_metrics' in body:
            error_metrics_array = [ErrorMetrics(_body=value) for value in body.get('error_metrics')]
            self.error_metrics = {value._model: value for value in error_metrics_array}
        else:
            self.error_metrics = None

    @property
    def data(self):
        result = {key: [] for key in self._columns}
        import csv
        import StringIO
        import datetime
        for row in csv.DictReader(StringIO.StringIO(self._csv_data), fieldnames=self._columns):
            for key in self._columns:
                value = row[key]
                if key == self._datetime_column:
                    try:
                        value = datetime.datetime.strptime(row[key],'%m/%d/%Y %H:%M:%S')
                    except ValueError:
                        value = datetime.datetime.strptime(row[key],'%m/%d/%Y')
                elif key == self._series_id_column:
                    pass # Just keep it as string
                else:
                    value = float(value)
                result[key].append(value)
        return result

    @property
    def frame(self):
        from pandas import DataFrame
        return DataFrame(self.data)

