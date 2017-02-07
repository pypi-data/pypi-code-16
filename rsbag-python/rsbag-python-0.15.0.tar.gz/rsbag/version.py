__version__ = '0.15.0'
__commit__ = 'gadfbc14'

def getVersion():
    """
    Returns a descriptive string for the version of the RSBag client API.
    """
    return "%s-%s" % (__version__, __commit__)
