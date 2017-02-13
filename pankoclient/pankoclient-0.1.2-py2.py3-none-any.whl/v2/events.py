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

from pankoclient import utils
from pankoclient.v2 import base

from six.moves import urllib

class EventManager(base.Manager):

    url = "v2/events"

    @staticmethod
    def build_simple_query_string(q):
        """Convert list of dicts and a list of params to query url format.
        This will convert the following:
            "[{field=this,op=le,value=34},
            {field=that,op=eq,value=foo,type=string}],
            ['foo=bar','sna=fu']"
        to:
            "q.field=this&q.field=that&
            q.op=le&q.op=eq&
            q.type=&q.type=string&
            q.value=34&q.value=foo&
            foo=bar&sna=fu"
        """
        if q:
            query_params = {'q.field': [],
                            'q.value': [],
                            'q.op': [],
                            'q.type': []}

            for query in q:
                for name in ['field', 'op', 'value', 'type']:
                    query_params['q.%s' % name].append(query.get(name, ''))

            # Transform the dict to a sequence of two-element tuples in fixed
            # order, then the encoded string will be consistent in Python 2&3.
            new_qparams = sorted(query_params.items(), key=lambda x: x[0])
            q = urllib.parse.urlencode(new_qparams, doseq=True)

        return q

    def list(self, query=None, limit=None, marker=None, sorts=None):
        """List Events
        :param query: Filter arguments for which Events to return
        :type query: list
        :param limit: maximum number of resources to return
        :type limit: int
        :param marker: the last item of the previous page; we return the next
                       results after this value.
        :type marker: str
        :param sorts: list of resource attributes to order by.
        :type sorts: list of str
        """
        pagination = utils.get_pagination_options(limit, marker, sorts)
        simple_query_string = EventManager.build_simple_query_string(query)

        url = self.url
        options = []
        if pagination:
            options.append(pagination)
        if simple_query_string:
            options.append(simple_query_string)
        if options:
            url += "?" + "&".join(options)
        return self._get(url).json()
