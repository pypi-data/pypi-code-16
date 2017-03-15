from errors import TransUnionAPIError, InvalidResponse
from transunion.utils.xml import dumps


def get_mock_body():
    """
    Construct a fake response body
    """
    body_dictionary = _get_mock_body_json()
    return dumps(body_dictionary)


def get_api_error_body():
    """
    Construct a fake error response body
    """
    body_dictionary = _get_api_error_body()
    return dumps(body_dictionary)


def raise_for_api_errors(data):
    try:
        indicative = data['pfs']['product']['subject']['subjectRecord']['indicative']  # noqa
    except KeyError:
        raise InvalidResponse(data=data)
    else:
        if type(indicative) not in [list, dict]:
            raise TypeError('indicative should be a list or dictionary, not {}'.format(str(type(indicative))))  # noqa
        elif 'error' in indicative:
            msg = indicative['error']
            raise TransUnionAPIError(msg)


def _get_mock_body_json():
    """
    fake response, data copied from TransUnion API Document
    """
    body = {
        'pfs':
            {
                '__xmlns__': "http://www.transunion.com/namespace/pfs/v4",
                '__xmlns:xsi__': "http://www.w3.org/2001/XMLSchema-instance",
                '__xsi:schemaLocation__': "http://www.transunion.com/namespace pfsV4.xsd",   # noqa
                'document': 'response',
                'version': '4.0',
                'transactionControl': {
                    'subscriber': {
                        'industryCode': 'Z',
                        'memberCode': '01497225',
                        'inquirySubscriberPrefixCode': '0605',
                        'password': 'PWD'
                    },
                    'userKey': 'jandDoe123',
                    'queryType': 'CR',
                    'permissiblePurpose': {
                        'endUser': {
                            'organization': None
                        }
                    },
                    'outputFormat': 'XML',
                    'referenceID': '1223929ABCD'
                },
                'product': {
                    'subject': {
                        'subjectRecord': {
                            'indicative': [
                                {
                                    '__source__': 'input',
                                    'name': {
                                        'person': {
                                            'first': 'SHELLY',
                                            'middle': None,
                                            'last': 'LONGS'
                                        }
                                    },
                                    'address': {
                                        'street': {
                                            'unparsed': '8566 E CHEERS AV'
                                        },
                                        'location': {
                                            'ciy': 'FANTASY LSLAND',
                                            'state': 'IL',
                                            'zipCode': '60750'
                                        }
                                    },
                                    'socialSecurity': {
                                        'number': '666987654'
                                    },
                                    'dateOfBirth': '1980-10-10'
                                },
                                {
                                    '__source__': 'file',
                                    'name': {
                                        'person': {
                                            'first': 'SHELLY',
                                            'middle': None,
                                            'last': 'LONGS'
                                        }
                                    },
                                    'address': {
                                        'street': {
                                            'unparsed': {
                                                '__val__': '5866 E CHEERS AV',
                                                '__DisplayColor__': 'RED'
                                            },
                                            'number': '5866',
                                            'preDirectional': 'E',
                                            'name': 'CHEERS',
                                            'postDirectional': None,
                                            'type': 'AV',
                                            'unit': None,
                                        },
                                        'location': {
                                            'ciy': 'FANTASY LSLAND',
                                            'state': 'IL',
                                            'zipCode': '60750'
                                        },
                                        'previousAddresses': {
                                            'address': {
                                                'status': 'previous',
                                                'street': {
                                                    'unparsed': '1234 E HOWARD ST',  # noqa
                                                    'number': '1234',
                                                    'preDirectional': 'E',
                                                    'name': 'HOWARD',
                                                    'postDirectional': None,
                                                    'type': 'ST',
                                                    'unit': None
                                                },
                                                'location': {
                                                    'city': 'FANTASY ISLAND',
                                                    'state': 'IL',
                                                    'zipCode': 60750
                                                }
                                            }
                                        },
                                        'phone': None,
                                        'socialSecurity': {
                                            'number': {
                                                '__val__': 666092811,
                                                '__DisplayColor__': 'RED'
                                            }
                                        },
                                        'dateOfBirth': '1966-08-01'
                                    }
                                }
                            ],
                            'calculations': {
                                'dti': 30,
                                'residualIncome': '376',
                                'fpl': 115,
                                'availableCredit': 812,
                                'estHouseholdIncome': 0,
                                'estHouseholdSize': 1,
                            },
                            'scores': None,
                            'determinationStatus': {
                                'accuracy': {
                                    '__val__': 'Accurate',
                                    '__DisplayColor__': 'GREEN'
                                },
                                'financialAid': {
                                    '__val__': '100 Percent Charity LOW CREDIT',  # noqa
                                    '__DisplayColor__': 'GREEN'
                                },
                                'collection': {
                                    '__DisplayColor__': 'RED',
                                    '__val__': 'Not Likely to Pay with Mortgage',  # noqa
                                },
                                'riskIndicator': None,
                                'redFlag': None,
                                'warnings': None
                            },
                            'creditReport': {
                                'pullDate': '2012-03-20 11:53:29.673',
                            }
                        }
                    },
                    'billingRecord': {
                        'originatingSourceCode': None
                    }
                }
            }
    }

    return body


def _get_api_error_body():
    """
    fake error response, data copied from TransUnion API Document
    """
    body = {
        'pfs':
            {
                '__xmlns__': "http://www.transunion.com/namespace/pfs/v4",
                '__xmlns:xsi__': "http://www.w3.org/2001/XMLSchema-instance",
                '__xsi:schemaLocation__': "http://www.transunion.com/namespace pfsV4.xsd",  # noqa
                'document': 'request',
                'version': '2.0',  # inconsistent version number in api doc
                'transactionControl': {
                    'subscriber': {
                        'industryCode': 'M',
                        'memberCode': '03346792',
                        'inquirySubscriberPrefixCode': None,
                        'password': 'PSWD'
                    },
                    'userKey': 'jandDoe123',
                    'queryType': 'CR',
                },
                'product': {
                    'subject': {
                        'subjectRecord': {
                            'indicative': {
                                'error': {
                                    '__val__': "Missing or Invalid: inquirySubscriberPrefixCode Transaction not Processed",  # noqa
                                    '__errorcode__': '1108,1109'
                                }
                            },
                        }
                    },
                }
            }
    }

    return body
