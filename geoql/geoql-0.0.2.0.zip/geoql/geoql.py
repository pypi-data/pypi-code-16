###############################################################################
## 
## geoql.py
##
##   Library for performing queries and transformations on GeoJSON data (with
##   emphasis on support for abstract graph representations).
##
##   Web:     github.com/data-mechanics/geoql
##   Version: 0.0.2.0
##
##

import types
import json
import geojson
import geopy.distance
from tqdm import tqdm

###############################################################################
##

"""
A GeoQL error is a general-purpose catch-all for any usage error.
"""
class GeoQLError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def match(value, query):        
    if type(query) in [str, int, float, type(None)]:
        return value == query
    elif type(query) == dict and len(query.keys()) == 1:
        for op in query:
            if op == "$eq": return value == query[op]
            elif op == "$lt": return value < query[op]
            elif op == "$lte": return value <= query[op]
            elif op == "$gt": return value > query[op]
            elif op == "$gte": return value >= query[op]
            elif op == "$ne": return value != query[op]
            elif op == "$in": return value in query[op]
            elif op == "$nin": return value not in query[op]
            else: GeoQLError("Not a valid query operator: " + op)
    else:
        raise GeoQLError("Not a valid query: " + str(query))

def features_properties_null_remove(obj):
    features = obj['features']
    for i in tqdm(range(len(features))):
        properties = features[i]['properties']
        features[i]['properties'] = {p:properties[p] for p in properties if properties[p] is not None}
    return obj

def features_tags_parse_str_to_dict(obj):
    features = obj['features']
    for i in tqdm(range(len(features))):
        tags = features[i]['properties'].get('tags')
        if tags is not None:
            try:
                tags = json.loads("{" + tags.replace("=>", ":") + "}")
            except:
                try:
                    tags = eval("{" + tags.replace("=>", ":") + "}")
                except:
                    tags = None
        if type(tags) == dict:
            features[i]['properties']['tags'] = {k:tags[k] for k in tags}
        elif tags is None and 'tags' in features[i]['properties']:
            del features[i]['properties']['tags']
    return obj

def features_keep_by_property(obj, query):
    features_keep = []
    for feature in tqdm(obj['features']):
        if all([match(feature['properties'].get(prop), qry) for (prop, qry) in query.items()]):
            features_keep.append(feature)
    obj['features'] = features_keep
    return obj

def features_keep_within_radius(obj, center, radius, units):
    features_keep = []
    for feature in tqdm(obj['features']):
        if all([getattr(geopy.distance.vincenty((lat,lon), center), units) < radius for (lon,lat) in geojson.utils.coords(feature)]):
            features_keep.append(feature)
    obj['features'] = features_keep
    return obj

def features_node_edge_graph(obj):
    points = {}
    features = obj['features']
    for feature in tqdm(obj['features']):
        for (lon, lat) in geojson.utils.coords(feature):
            points.setdefault((lon, lat), 0)
            points[(lon, lat)] += 1
    points = [p for (p, c) in points.items() if c > 1]
    features = [geojson.Point(p) for p in points]

    # For each feature, split it into "edge" features
    # that occur between every point.
    for f in tqdm(obj['features']):
        seqs = []
        seq = []
        for point in geojson.utils.coords(f):
            if len(seq) > 0:
                seq.append(point)
            if point in points:
                seq.append(point)
                if len(seq) > 1 and seq[0] in points:
                    seqs.append(seq)
                    seq = [point]
        for seq in seqs:
            features.append(geojson.Feature(geometry={"coordinates":seq, "type":f['geometry']['type']}, properties=f['properties'], type=f['type']))

    obj['features'] = features
    return obj

## eof