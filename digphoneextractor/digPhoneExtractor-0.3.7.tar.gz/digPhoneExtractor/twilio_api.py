# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-10-13 14:51:29
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-02 14:44:06

# Download the Python helper library from twilio.com/docs/python/install
from twilio.rest.lookups import TwilioLookupsClient
from twilio.rest.exceptions import TwilioRestException

# Your Account Sid and Auth Token from twilio.com/user/account

account_sid = ""
auth_token = ""

client = TwilioLookupsClient(account_sid, auth_token)

def load_phone_number(phone_number):

    """ client.phone_numbers.get

    (check detail at https://github.com/twilio/twilio-python/blob/master/twilio/rest/resources/lookups/phone_numbers.py)

    return twilio.rest.resources.lookups.phone_numbers.PhoneNumber
    
    PhoneNumber Attributes:
    - phone_number: The phone number in normalized E.164 format, e.g. "+14158675309"
    - national_format: The phone number in localized format, e.g. "(415) 867-5309"
    - country_code: The ISO 3166-1 two-letter code for this phone number's country, e.g. "US" for United States
    - carrier: A dictionary of information about the carrier responsible for this
        number, if requested.Contains the following:

        - mobile_country_code: the country code of the mobile carrier.
        Only populated if the number is a mobile number.
        - mobile_network_code: the network code of the mobile carrier.
        Only populated if the number is a mobile number.
        - name: the name of the carrier.
        - type: the type of the number ("mobile", "landline", or "voip")
        - error_code: the error code of the carrier info request, if one
        occurred

    """
    try:
        number = client.phone_numbers.get(phone_number, include_carrier_info=True)

        ans = {}
        ans.setdefault('phone_number', number.phone_number)
        ans.setdefault('national_format', number.national_format)
        ans.setdefault('country_code', number.country_code)
        ans.setdefault('carrier', number.carrier)

    except TwilioRestException as e:
        if e.code == 20404:
            """
            When the Twilio Python library encounters a 404 it will throw a "TwilioRestException". 
            The error code for this is 20404, so if we want to write a function that validates phone numbers we can check to see if an exception was raised with code 20404.
            """
            return {'error': 'NOT IN DATABASE'}
        else:
            print e
            return {'error': 'NOT IN DATABASE'}
            # raise e

    else:
        return ans
    

if __name__ == '__main__':
    import json
    phone_number = "+61396991047"
    # phone_number = "2133790691"
    # 9921488433
    # 971552602207
    # 431579430138
    # 310504188822
    ans = load_phone_number(phone_number)
    print json.dumps(ans, indent=4)
