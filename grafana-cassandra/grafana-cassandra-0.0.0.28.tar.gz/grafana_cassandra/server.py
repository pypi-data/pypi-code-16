import json
from datetime import timedelta, datetime

import cherrypy

from config.config import Config
from db_clients.cassandra_client import CassandraClient

cherrypy.log.screen = True


class ClusterList(object):
    def __init__(self):
        self.cluster_list = []

class Root(object):
    """
    object that maps http requests to methods.
    /index = '/'
    /query = '/query'
    etc...
    """
    def __init__(self):
        self.config = Config()
        print('connectiing to cassandra...')
        self.cassandra_client = CassandraClient(self.config)
        self.cassandra_client.connect()
        # Query used to get actual service metrics from cassandra
        self.metrics_query = (
            """
            SELECT *
            FROM {table}
            WHERE host=%s
                AND service=%s
                AND bucket_time=%s
                ORDER BY time ASC;
            """)
        # Query used to get metric service names, is later filtered to show only used metrics
        self.select_query_template = (
            """
            SELECT metric
            FROM %(keyspace)s.%(table)s
            WHERE host=%(host)s
                AND service=%(
            """)

    @cherrypy.expose
    def index(self):
        return 'woot'

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def query(self):
        response = QueryPOSTJson(**cherrypy.request.json)  # map response json to object
        btime = response.range.after
        new_targets = []
        formatted_results = {}
        for target in response.targets:
            print (target)
            for host in self.config.hosts.hostnames:
                for t in str(target['target'].split('.')[0]).strip('{}').split(','):
                    if t in self.config.hosts.hostnames:
                        if t == host:
                            new_targets.append([host, target['target'].split('.')[-1]])
                    else:
                        new_targets.append([host, target['target'].split('.')[-1]])
        for target in new_targets:
            futures = []
            service = target[1]
            cur_bucket = (btime.replace(minute=btime.minute - btime.minute % 5,
                                        second=0,
                                        microsecond=0)) - timedelta(minutes=5)
            while True:
                cur_bucket += timedelta(minutes=5)
                query = """
                SELECT metric, time
                FROM monitoring.ingest
                WHERE host ='{host}'
                    AND service ='{service}'
                    AND bucket_time = '{bucket_time}+0000'
                """
                futures.append(self.cassandra_client.session.execute_async(query.format(
                    host=target[0], service=service, bucket_time=cur_bucket
                )))
                if cur_bucket > response.range.before:
                    break
            formatted_results[target[0]] = [row for future in futures for row in future.result()]

        # generate a json to send to grafana as a response
        # out_json should be of the following format
        # [
        #     {
        #         'target': response.targets[0]['target'],
        #         'datapoints': [
        #             [ <metric>, <timestamp in ms> ]
        #             [ <metric>, <timestamp in ms> ]
        #         ]
        #     }
        # ]
        return json.dumps(
                [
                    {
                        'target': target, 'datapoints': [
                            [
                                # Generate a time series data model of metrics, timestamp is in milliseconds
                                r[0],
                                # TODO: make this statement TZ aware
                                int((r.time + timedelta(hours=10)).strftime('%s'))*1000
                            ] for r in results]
                        # do this for every metric we gathered
                    } for target, results in formatted_results.iteritems()
                ]
            )

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def search(self, *args, **kwargs):
        """
        Invoked when selecting a metric to show on the Dashboard.
        example output:
        ['<metric1>', '<metric2>']
        :return: JSON representing the list of metrics
        """
        print(cherrypy.request.params)
        print(cherrypy.request.json)
        print(args)
        print(kwargs)
        # if 'name' was a key in the recieved json, this is a templating query
        if 'name' in cherrypy.request.json.keys():
            # figure out which query we actually want
            if cherrypy.request.json['name'] == 'host':
                # return a list of host names
                return json.dumps({h: h for h in self.config.hosts.hostnames})

        # otherwise this is a search for available metrics
        return json.dumps(self.get_fetchable_metrics())


    @cherrypy.expose
    def annotation(self):
        """
        yet to be explored, i have nfi what this does yet - i think it marks events on the graph??
        :return: a json of some description.... would be great if it was documented.
        """
        return json.dumps(['metrics', 'host'])

    def get_fetchable_metrics(self):
        return self.config.hosts.services

    def get_hosts(self):

        hosts = [host.host for host in self.cassandra_client.session.execute(
            """
            SELECT DISTINCT host
            FROM monitoring.test10"""
        )]
        return hosts

def force_parse_headers():
    """
    Because we dont actually get passed a query string, this gets the full URL requested
    which has the templating variables in it, and returns what would have been a list of
    query parameters in the query string.
    :return: dict { 'var-name': int(value)|None, ...} or empty dict
    """
    headers = {}
    try:
        for key_value in cherrypy.request.headers['Referer'].split('?')[1].split('&'):
            key_value = key_value.split('=')
            try:
                headers[key_value[0]] = int(key_value[1]) if len(key_value) > 1 else True
            except ValueError:
                headers[key_value[0]] = key_value[1] if len(key_value) > 1 else True
    except:
        return {}
    return headers


class QueryPOSTJson(object):
    """
    This maps the POST query from grafana when it sends a /query request.
    """
    def __init__(self, format, interval, range, rangeRaw, panelId, targets, maxDataPoints, cacheTimeout=None):
        self.format = format
        self.interval = interval
        self.range = TimeRange(range)
        self.range_raw = rangeRaw
        self.panel_id = panelId
        self.targets = targets
        self.max_data_points = maxDataPoints


class TimeRange(object):
    """
    This maps the nested 'range' dict to an object.
    """
    def __init__(self, r):
        self.before = grafana_dt_to_dt(r['to'])
        self.after = grafana_dt_to_dt(r['from'])


def grafana_dt_to_dt(g):
    """
    Convert the strange datetime string grafana uses to a python datetime object
    :param g: grafana datetime string
    :return: python datetime object
    """
    return datetime.strptime(g, "%Y-%m-%dT%H:%M:%S.%fZ")


def dt_to_dt_string(dt):
    """
    Converts python datetime object to a datetime string to be used as query parameters for metrics
    :param dt: python datetime object
    :return: datetime string ssasd
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def main():
    cherrypy.tree.mount(
            Root(), '/', cherrypy.config.update(
                    {'tools.sessions.on': True,
                     'tools.sessions.timeout': 10}))

    cherrypy.engine.signals.subscribe()
    cherrypy.engine.start()
    cherrypy.engine.block()
    if hasattr(cherrypy.engine, 'signal_handler'):
        cherrypy.engine.signal_handler.subscribe()


if __name__ == '__main__':
    main()
