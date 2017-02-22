""" standard """
import types
import urllib

""" custom """
from Config.ResourceRegexes import md5_re, sha1_re, sha256_re
from Config.ResourceType import ResourceType

# group type to resource type mapping
g_type_to_r_type = {
    'Address': ResourceType.EMAILS,
    'Adversary': ResourceType.ADVERSARIES,
    'Document': ResourceType.DOCUMENTS,
    'Email': ResourceType.EMAILS,
    'Incident': ResourceType.INCIDENTS,
    'Signature': ResourceType.SIGNATURES,
    'Threat': ResourceType.THREATS}

# indicator type to resource type mapping
i_type_to_r_type = {
    'Address': ResourceType.ADDRESSES,
    'EmailAddress': ResourceType.EMAIL_ADDRESSES,
    'File': ResourceType.FILES,
    'Host': ResourceType.HOSTS,
    'URL': ResourceType.URLS,
    'Custom': ResourceType.CUSTOM_INDICATORS}

# uri attributes
resource_uri_attributes = {
    'ADDRESSES': 'addresses',
    'EMAIL_ADDRESSES': 'emailAddresses',
    'FILES': 'files',
    'HOSTS': 'hosts',
    'URLS': 'urls',
}


def get_hash_type(indicator):
    """Get hash type from an indicator."""
    if md5_re.match(indicator):
        return 'MD5'
    elif sha1_re.match(indicator):
        return 'SHA1'
    elif sha256_re.match(indicator):
        return 'SHA256'


def get_resource_type(indicators_regex, indicator):
    """ Get resource type enum from an indicator. """
    if indicator is None:
        return None

    for indicator_type, regex in indicators_regex.items():
        for rex in regex:
            match = rex.match(indicator)
            if match and match.group(0) == indicator:
                return ResourceType[indicator_type]
    # if it's none of these, it's custom
    return ResourceType.CUSTOM_INDICATORS


def get_resource_group_type(group_type):
    """Get resource type enum from a group type."""
    return g_type_to_r_type[group_type]


def get_resource_indicator_type(indicator_type):
    """Get resource type enum from a indicator type. If it's not one of the named types, it's custom"""
    return i_type_to_r_type[indicator_type] if indicator_type in i_type_to_r_type else ResourceType.CUSTOM_INDICATORS


def get_indicator_uri_attribute(indicators_regex, indicator):
    """ """
    for indicator_type, regex in indicators_regex.items():
        for rex in regex:
            if rex.match(indicator):
                return resource_uri_attributes[indicator_type]
    return None


def uni(data):
    """ convert to unicode when appropriate """
    if data is None or not isinstance(data, types.StringTypes):
        return data
    elif isinstance(data, unicode):
        return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
    elif not isinstance(data, unicode):
        return unicode(data, 'utf-8', errors='ignore')


def urlsafe(data):
    """ url encode value for safe request """
    return urllib.quote(data, safe='~')


def urlunsafe(data):
    """ url encode value for safe request """
    return urllib.unquote(data)


def validate_indicator(indicators_regex, indicator):
    """ """
    for indicator_type, regex in indicators_regex.items():
        for rex in regex:
            if rex.match(str(indicator)):
                return True
    return False


def validate_rating(rating):
    """ """
    if rating in ["1.0", "2.0", "3.0", "4.0", "5.0", 0, 1, 2, 3, 4, 5]:
        return True

    # todo - make this a bit more robust, 0?
    return False
