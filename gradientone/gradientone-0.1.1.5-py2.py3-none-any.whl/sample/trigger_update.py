import json
import requests

COMPANYNAME = 'Acme'
DOMAIN = 'gradientone-dev2.appspot.com'
headers = {}
headers['Content-type'] = 'application/json'

payload = {
    "command": {
        "reload": True,
        "package": "gradientone",
        "module_name": "gradientone",
        "version": "0.1.1.2"
    }
}

session = requests.session()
url = "https://" + DOMAIN + "/client_updates"
print "posting to url:", url
response = session.post(url, headers=headers, data=json.dumps(payload))
print "response", response
print "response.text", response.text

# To GET the update like a controller would:
# response = session.get(url)
# print "response", response
# print "response.text", response.text
