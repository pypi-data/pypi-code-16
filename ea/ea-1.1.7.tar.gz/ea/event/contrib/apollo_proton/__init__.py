try:
    from ea.event.contrib.apollo_proton.adapter import ProtonAdapter
    from ea.event.contrib.apollo_proton.transport import ProtonTransport
except ImportError as e:
    if e.name != 'proton':
        raise
    from ea.utils import MissingDependency

    ProtonAdapter = MissingDependency('proton')
    ProtonTransport = MissingDependency('proton')
