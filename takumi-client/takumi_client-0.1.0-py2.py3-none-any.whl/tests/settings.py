CLIENT_SETTINGS = {
    'test': {
        'service_name': 'PingService',
        'thrift_file': './tests/ping.thrift',
        # 'hosts_class': 'takumi_client.hosts.RedisHosts',
        # 'redis_dsn': 'redis://localhost:6379',
        # 'redis_key': 'test_hosts',
        'hosts': [
            ('localhost', 1990),
            ('localhost', 8010),
            ('localhost', 1890)
        ]
    }
}
