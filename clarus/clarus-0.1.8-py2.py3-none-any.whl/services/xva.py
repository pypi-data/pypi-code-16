import clarus.services

def adjustment(output=None, **params):
    return clarus.services.api_request('XVA', 'Adjustment', output=output, **params)

def funding(output=None, **params):
    return clarus.services.api_request('XVA', 'Funding', output=output, **params)

