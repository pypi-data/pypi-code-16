import datetime
from urllib.parse import (urljoin, urlparse, parse_qs, urlencode, urlunparse)
from urllib.request import (urlopen)
from posixpath import join as posixjoin
from xml.etree import ElementTree as ET

class MarketingVillasUrls(object):
    # Base Components
    BASE_URL = "http://ws.marketingvillas.com/"
    BASE_PATH = "/partners.asmx"

    # Individual API Paths
    TIME_TOKEN_ENDPOINT = ("/Security_GetTimeToken", [],)
    MD5_TOKEN_ENDPOINT = ("/Security_GetMD5Hash", ["p_ToHash"],)
    VILLA_LIST_ENDPOINT = ("/getMVLVillaList", ["p_Token", "p_UserID"],)
    VILLA_RATES_ENDPOINT = ("/getVillaRates", ["p_Token", "p_UserID", "p_VillaID"],)


class MarketingVillasApi(object):
    """
    This class encapsulates the MarketingVillas API.

    Each API endpoint is associated with two methods of this class, both of
    which share a similar name to the API endpoint that they work with:
    
    1.) A public method intended for general use, which returns the data
        retrieved from the endpoint in a nominally user/code-friendly
        format specific to that endpoint (e.g. a dictionary, or a plain
        string).

    2.) A private method intended for internal and specialist use, which
        does nothing more than make a call to the API with the right
        parameters, returning the bytes content of the response as-is
        (typically containing XML-formatted data). These private methods
        bear the same signature as their public counterparts, except the
        method identifier is prefixed with a single underscore.
    """

    def __init__(self, user_id: str, password: str):
        self.user_id = user_id
        self.password = password


    # Utilities and common operations

    @classmethod
    def _construct_endpoint(cls, endpoint: tuple, get_params: dict={}) -> str:
        """
        This function handles construction of API endpoints to be used for
        making HTTP requests. Combined with the `MarketingVillasUrls`, this
        function also verifies that the required GET parameters are being passed.
        """
        path = endpoint[0]
        param_keys = endpoint[1]

        # Verify required keys are provided
        for key in param_keys:
            if key not in get_params:
                raise KeyError(key)

        joined_endpoint = urljoin(MarketingVillasUrls.BASE_URL, posixjoin(MarketingVillasUrls.BASE_PATH, path.lstrip("/")))
        parsed_endpoint = urlparse(joined_endpoint)
        query_string = urlencode(get_params)
        result = urlunparse(parsed_endpoint._replace(query=query_string))
        return result

    @classmethod
    def _make_request(cls, url: str) -> bytes:
        with urlopen(url) as response:
            content = response.read()
        return content

    @classmethod
    def _raw_bytes_to_tree(cls, raw: bytes) -> ET.ElementTree:
        return ET.fromstring(raw.decode("utf8"))


    # API endpoints wrapped in member functions

    def _get_time_token(self) -> bytes:
        request_uri = self._construct_endpoint(MarketingVillasUrls.TIME_TOKEN_ENDPOINT, {})
        resp = self._make_request(request_uri)
        return resp

    def get_time_token(self) -> str:
        tree = self._raw_bytes_to_tree(self._get_time_token())
        time_token = tree.text
        return time_token

    def _get_md5_token(self) -> bytes:
        tohash = "|".join( [self.user_id, self.password, self.get_time_token()] )
        request_uri = self._construct_endpoint(MarketingVillasUrls.MD5_TOKEN_ENDPOINT,
                {
                    "p_ToHash": tohash
                })
        resp = self._make_request(request_uri)
        return resp

    def get_md5_token(self) -> str:
        tree = self._raw_bytes_to_tree(self._get_md5_token())
        md5_token = tree.text
        return md5_token

    def _get_villa_list(self) -> bytes:
        request_uri = self._construct_endpoint(MarketingVillasUrls.VILLA_LIST_ENDPOINT,
                {
                    "p_Token": self.get_md5_token(),
                    "p_UserID": self.user_id
                })
        resp = self._make_request(request_uri)
        return resp

    def get_villa_list(self) -> list:
        tree = self._raw_bytes_to_tree(self._get_villa_list())
        villas_element = tree
        villas_children = villas_element.getchildren()
        villas_list = [ {
            "villa_id": villa.attrib["villaid"],
            "sort_name": villa.attrib["sortname"],
            "base_url": villa.attrib["baseurl"],
            "name": villa.text
        } for villa in villas_children ]
        return villas_list

    def _get_villa_rates(self, villa_id: str) -> bytes:
        request_uri = self._construct_endpoint(MarketingVillasUrls.VILLA_RATES_ENDPOINT,
                {
                    "p_Token": self.get_md5_token(),
                    "p_UserID": self.user_id,
                    "p_VillaID": villa_id
                })
        return self._make_request(request_uri)

    def get_villa_rates(self, villa_id: str) -> dict:

        def parse_date(datestr):
            return datetime.datetime.strptime(datestr, "%Y-%m-%dT00:00:00")

        tree = self._raw_bytes_to_tree(self._get_villa_rates(villa_id))
        rates_element = tree.getchildren()[0]
        rates_children = rates_element.getchildren()
        villa_rates_obj = {
            "villa_id": villa_id,
            "rate_name": rates_children[0].text,
            "rates": [ {
                "from": parse_date(rate.find("From").text),
                "to": parse_date(rate.find("To").text),
                "amount": float(rate.find("Amount").text),
                "min_stay": int(rate.find("MinimumNightStay").text),
                "percent_tax": float(rate.find("PercentTax").text),
                "percent_rate": float(rate.find("PercentRate").text)
            } for rate in rates_children[1:] ]
        }
        return villa_rates_obj

