from requests.structures import LookupDict

_codes = {
    0: ('ok',),
    4100: ('param_invalid',),
    4101: ('access_key_invalid',),
    4103: ('resource_unauthorized',),
    4104: ('resource_not_found',),
    4105: ('action_disallow',),
    4110: ('request_format_invalid',),
    4113: ('quota_not_enough',),
    5000: ('server_error',),
    5001: ('actions_totally_failed',),
    5002: ('actions_partially_failed',),
}

codes = LookupDict(name='ret_codes')

for (code, titles) in list(_codes.items()):
    for title in titles:
        setattr(codes, title, code)
