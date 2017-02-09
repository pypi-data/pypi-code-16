import json
import twilio
from twilio.rest import Client


account_sid = ""
auth_token = ""



# client = twilio.rest.Client(username=account_sid, password=auth_token)
# ph = client.lookups.phone_numbers("+16502530000").fetch(add_ons="payfone_tcpa_compliance",add_ons_data={"payfone_tcpa_compliance.RightPartyContactedDate":"20160101"})
# print(ph.add_ons)

# whitepages_pro_caller_id
# nextcaller_advanced_caller_id


client = twilio.rest.Client(username="", password="")

ph = client.lookups.phone_numbers("+16502530000").fetch(add_ons="nextcaller_advanced_caller_id")
print json.dumps(ph.add_ons, indent=4)