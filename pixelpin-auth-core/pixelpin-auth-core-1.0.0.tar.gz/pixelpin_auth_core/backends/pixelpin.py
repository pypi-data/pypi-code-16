from .open_id_connect import OpenIdConnectAuth
import json


class PixelPinOpenIDConnect(OpenIdConnectAuth):
    """PixelPin OpenID Connect authentication backend"""
    name = 'pixelpin-openidconnect'
    ID_KEY = 'sub'
    AUTHORIZATION_URL = 'https://logincallum.pixelpin.co.uk/connect/authorize'
    ACCESS_TOKEN_URL = 'https://logincallum.pixelpin.co.uk/connect/token'
    OIDC_ENDPOINT = 'https://logincallum.pixelpin.co.uk'
    JWKS_URI = 'https://logincallum.pixelpin.co.uk/.well-known/jwks'
    ACCESS_TOKEN_METHOD = 'POST'
    REQUIRES_EMAIL_VALIDATION = False
    EXTRA_DATA = [
        ('sub', 'id'),
        ('gender', 'gender'),
        ('birthdate', 'birthdate'),
        ('phone_number','phone_number'),
        ('street_address', 'street_address'),
        ('locality', 'locality'),
        ('region', 'region'),
        ('postal_code', 'postal_code'),
        ('country', 'country'),

    ]

    def get_user_details(self, response):
        """Return user details from PixelPin account"""

        if response.get('address') is None:
            street_address = ''
            locality = ''
            region = ''
            postal_code = ''
            country = ''
        else:
            decodedAddress = json.loads(response.get('address'))
            street_address = decodedAddress['street_address'] 
            locality = decodedAddress['locality'] 
            region = decodedAddress['region'] 
            postal_code = decodedAddress['postal_code'] 
            country = decodedAddress['country'] 

        first_name = response.get('given_name')
        last_name = response.get('family_name')
        sub = response.get('sub')

        username = first_name + last_name + sub

        return {'username': username,
                'email': response.get('email'),
                'fullname': response.get('given_name') + response.get('family_name'),
                'first_name': response.get('given_name'),
                'last_name': response.get('family_name'),
                'gender': response.get('gender'),
                'birthdate': response.get('birthdate'),
                'phone_number': response.get('phone_number'),
                'street_address': street_address,
                'locality': locality,
                'region': region,
                'postal_code': postal_code,
                'country': country}
    
	
    def user_data(self, access_token, *args, **kwargs):
        return self.get_json('https://logincallum.pixelpin.co.uk/connect/userinfo', headers={
            'Authorization': 'Bearer {0}'.format(access_token)
        })
