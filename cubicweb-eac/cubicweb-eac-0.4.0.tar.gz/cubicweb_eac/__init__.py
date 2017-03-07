"""cubicweb-eac application package

Implementation of Encoded Archival Context for CubicWeb
"""


# EAC mappings

TYPE_MAPPING = {
    'corporateBody': u'authority',
    'person': u'person',
    'family': u'family',
}

MAINTENANCETYPE_MAPPING = {
    'created': u'create',
    'revised': u'modify',
}

# Order matters for this one in order to export correctly
ADDRESS_MAPPING = [
    ('StreetName', 'street'),
    ('PostCode', 'postalcode'),
    ('CityName', 'city'),
]
