import clarus.services

def df(output=None, **params):
    return clarus.services.api_request('Market', 'DF', output=output, **params)

def fxrates(output=None, **params):
    return clarus.services.api_request('Market', 'FXRates', output=output, **params)

def pardv01(output=None, **params):
    return clarus.services.api_request('Market', 'ParDV01', output=output, **params)

def parrates(output=None, **params):
    return clarus.services.api_request('Market', 'ParRates', output=output, **params)

def zerorates(output=None, **params):
    return clarus.services.api_request('Market', 'ZeroRates', output=output, **params)

