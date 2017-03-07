import http.client, urllib.request, urllib.parse, urllib.error, base64, json
from django.conf import settings


class NV_API:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.entry_point = 'api.novaposhta.ua'
        self.params = urllib.parse.urlencode({})

    def get_connection(self):
        return http.client.HTTPConnection(self.entry_point)

    def get_response(self, model_name, called_method, method_properties={}, method='POST'):
        conn = self.get_connection()

        data = {
            'modelName': model_name,
            'calledMethod': called_method,
            'apiKey': self.api_key,
            'methodProperties': method_properties,
        }

        conn.request(
            method,
            '/v2.0/json/AddressGeneral/getWarehouses?%s' % self.params,
            json.dumps(data),
            self.headers,
        )
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return json.loads(str(data, 'utf-8'))

    def get_areas(self, properties={}):
        result = self.get_response('Address', 'getAreas', properties)
        return result['data']

    def get_company_cities(self, properties={}):
        result = self.get_response('AddressGeneral', 'getCities', properties)
        return result['data']

    def get_settlements(self, properties={}):
        result = self.get_response('AddressGeneral', 'getSettlements', properties)
        return result['data']

    def get_offices(self, properties={}):
        result = self.get_response('AddressGeneral', 'getWarehouses', properties)
        return result['data']


def update_areas_table():
    from .models import Area
    nv = NV_API(settings.PCART_NOVAPOSHTA_API_KEY)
    areas = nv.get_areas()
    for area in areas:
        Area.objects.update_or_create(
            id=area['Ref'],
            defaults={
                'description': area['Description'],
            },
        )


def update_cities_table():
    from .models import City
    nv = NV_API(settings.PCART_NOVAPOSHTA_API_KEY)
    cities = nv.get_company_cities()
    for city in cities:
        City.objects.update_or_create(
            id=city['Ref'],
            defaults={
                'description': city['Description'],
                'description_ru': city['DescriptionRu'],
                'area_id': city['Area'],
            },
        )


def update_offices_table():
    from .models import Office
    nv = NV_API(settings.PCART_NOVAPOSHTA_API_KEY)
    offices = nv.get_offices()
    for office in offices:
        Office.objects.update_or_create(
            id=office['Ref'],
            defaults={
                'description': office['Description'],
                'description_ru': office['DescriptionRu'],
                'city_id': office['CityRef'],
                'number': int(office['Number']),
                'sitekey': office['SiteKey'],
                'international_shipping': office['InternationalShipping'] == '1',
                'place_max_weight_allowed': office['PlaceMaxWeightAllowed'],
                'total_max_weight_allowed': office['TotalMaxWeightAllowed'],
                'pos_terminal': office['POSTerminal'] == '1',
                'post_finance': office['PostFinance'] == '1',
                'bicycle_parking': office['BicycleParking'] == '1',
                'phone': office['Phone'],
                'delivery': office['Delivery'],
                'reception': office['Reception'],
                'latitude': office['Latitude'],
                'longitude': office['Longitude'],
            }
        )


def update_nv_db():
    update_areas_table()
    update_cities_table()
    update_offices_table()
