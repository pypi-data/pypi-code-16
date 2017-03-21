# coding=utf-8
import os
from pkg_resources import get_distribution, DistributionNotFound


def get_dist():
    dist = get_distribution('missinglink-kernel')
    # Normalize case for Windows systems
    dist_loc = os.path.normcase(dist.location)
    here = os.path.normcase(__file__)

    if not here.startswith(os.path.join(dist_loc, 'missinglink')):
        # not installed, but there is another version that *is*
        raise DistributionNotFound

    return dist


def get_keywords():
    try:
        dist = get_dist()
    except DistributionNotFound:
        return None

    parsed_pkg_info = getattr(dist, '_parsed_pkg_info', None)

    if parsed_pkg_info is None:
        return None

    return parsed_pkg_info.get('Keywords')


def get_version():
    try:
        dist = get_dist()
    except DistributionNotFound:
        return None

    return dist.version
