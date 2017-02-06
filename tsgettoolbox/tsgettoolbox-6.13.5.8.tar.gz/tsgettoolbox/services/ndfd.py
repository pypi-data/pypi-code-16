
import datetime
from collections import defaultdict

from odo import odo, resource, convert
import pandas as pd
import requests

# NOAA NDFD - National Digital Forecast Service

class NDFD_XML(object):
    def __init__(self, url, **query_params):
        # Need to enforce time-series format
        self.url = url
        self.query_params = query_params

@resource.register(r'http://graphical\.weather\.gov/xml/sample_products/browser_interface/ndfdXMLclient\.php.*', priority=17)
def resource_ndfd(uri, **kwargs):
    return NDFD_XML(uri, **kwargs)

# Function to convert from NDFD_XML type to pd.DataFrame
@convert.register(pd.DataFrame, NDFD_XML)
def ndfd_xml_to_df(data, **kwargs):
    req = requests.get(data.url, params=data.query_params)
    req.raise_for_status()

    print(req.content)
    return pd.DataFrame()


if __name__ == '__main__':
    r = resource(
        r'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php',
        lat=38.99,
        lon=-77.01,
        begin='2015-07-30'
        )

    as_df = odo(r, pd.DataFrame)
    print('NDFD')
    print(as_df)

