import requests

def openurl(address):
    try:
        r = requests.get(address)
        r.raise_for_status()
        return r.text
    except requests.HTTPError as e:
        print("HTTPError = {}".format(r.status_code))
    except requests.ConnectionError as e:
        print("ConnectionError = {}".format(e))
    except Exception:
        import traceback
        print("Generic Exception: {}".format(traceback.format_exc()))
    print("Request to {} failed.".format(address))
    return "Failed"

def activateurl(address):
    try:
        r = requests.get(address)
        r.raise_for_status()
        return r
    except requests.HTTPError as e:
        print("HTTPError = {}".format(r.status_code))
    except requests.ConnectionError as e:
        print("ConnectionError = {}".format(e))
    except Exception:
        import traceback
        print("Generic Exception: {}".format(traceback.format_exc()))
    print("Request to {} failed.".format(address))
    return "Failed"
