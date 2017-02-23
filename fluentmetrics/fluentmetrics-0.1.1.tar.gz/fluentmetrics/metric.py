import logging
import arrow
import uuid
import boto3
import boto3.session

logger = logging.getLogger('metric')
logger.addHandler(logging.NullHandler())


class Timer(object):
    def __init__(self):
        self.start = arrow.utcnow()

    def elapsed(self):
        return arrow.utcnow() - self.start

    def elapsed_in_ms(self):
        return self.elapsed().total_seconds() * 1000

    def elapsed_in_seconds(self):
        return self.elapsed().total_seconds()


class FluentMetric(object):
    def __init__(self, **kwargs):
        self.metric_stream_id = kwargs.get('MetricStreamId', str(uuid.uuid4()))
        self.dimensions = []
        self.timers = {}
        self.dimension_stack = []
        self.with_dimension('MetricStreamId', self.metric_stream_id)
        profile = kwargs.get('Profile')
        if profile:
            session = boto3.session.Session(profile_name=profile)
            self.client = session.client('cloudwatch')
        else:
            self.client = boto3.client('cloudwatch')

    def with_namespace(self, namespace):
        self.namespace = namespace
        return self

    def with_dimension(self, name, value):
        self.dimensions.append({'Name': name, 'Value': value})
        return self

    def without_dimension(self, name):
        if not self.dimensions:
            return
        del self.dimensions[name]
        return self

    def with_timer(self, timer):
        self.timers[timer] = Timer()
        return self

    def without_timer(self, timer):
        if timer in self.timers.keys():
            del self.timers[timer]
        return self

    def get_timer(self, timer):
        if timer in self.timers.keys():
            return self.timers[timer]
        else:
            return None

    def push_dimensions(self):
        self.dimension_stack.append(self.dimensions)
        self.dimensions = {}
        self.dimensions['uuid'] = self.uuid
        return self

    def pop_dimensions(self):
        self.dimensions = self.dimension_stack.pop()
        return self

    def put_elapsed(self, **kwargs):
        tn = kwargs.get('TimerName')
        mn = kwargs.get('MetricName')
        if tn not in self.timers.keys():
            logger.warn('No timer named {}'.format(tn))
            return
        self.put_metric_data(Value=self.timers[tn].elapsed_in_ms(),
                             Unit='Milliseconds',
                             MetricName=mn)

    def put_count(self, **kwargs):
        mn = kwargs.get('MetricName')
        count = kwargs.get('Count', 1)
        self.put_metric_data(Value=count,
                             Unit='Count',
                             MetricName=mn)

    def put_metric_data(self, **kwargs):
        ts = kwargs.get('TimeStamp', arrow.utcnow()
                        .format('YYYY-MM-DD HH:mm:ss ZZ'))
        value = float(kwargs.get('Value'))
        unit = kwargs.get('Unit')
        md = []
        for dimension in self.dimensions:
            md.append({
                        'MetricName': kwargs.get('MetricName'),
                        'Dimensions': [dimension],
                        'Timestamp': ts,
                        'Value': value,
                        'Unit': unit

                    }
            )

        md.append({
                    'MetricName': kwargs.get('MetricName'),
                    'Dimensions': self.dimensions,
                    'Timestamp': ts,
                    'Value': value,
                    'Unit': unit
                  })

        logger.debug('put_metric_data: {}'.format(md))
        self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=md
        )
