import urllib2, json, requests, re
from base64 import encodestring

def getBiomarkerLinks(biomarker, idDataSource):
    if not idDataSource:
        return None
    if idDataSource.strip() == "":
        return None
        
    r = requests.get(idDataSource+"/"+biomarker, headers={'Accept': 'application/json'})

    j= r.text
    j=j.replace("'", '"')
    j=j.replace('u"', '"')
    j=j.strip()
    
    jsonresults = None
    if j != "":
        try:
            jsonresults = json.loads(j)
        except ValueError:
            pass
    return jsonresults
