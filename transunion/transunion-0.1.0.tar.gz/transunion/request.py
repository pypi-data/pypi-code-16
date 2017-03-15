from collections import OrderedDict


def add_transunion_info(config, applicant_info):
    api_request_info = {
        'pfs': OrderedDict([
            ('__xmlns__', 'http://www.transunion.com/namespace/pfs/v4'),
            ('__xmlns:xsi__', "http://www.w3.org/2001/XMLSchema-instance"),
            ('__xsi:schemaLocation__',
             "http://www.transunion.com/namespace pfsV4.xsd"),
            ('document', _get_document()),
            ('version', _get_pfs_version()),
            ('transactionControl', _get_transaction_control(config)),
            ('product', _get_product(applicant_info))
        ])
    }
    return api_request_info


def _get_document():
    """
    This element indicates the type of message, here is 'request'
    """
    return 'request'


def _get_pfs_version():
    """
    Indicate the version of PFS XML you are using
    """
    return '4.0'


def _get_transaction_control(config):
    """
    The <transactionControl> element contains the key information about the
    subscriber who is making the request
    """
    subscriber_info = {
        'industryCode': config.industry_code,
        'memberCode': config.member_code,
        'inquirySubscriberPrefixCode': config.prefix_code,
        'password': config.sub_password,
        # CR returns Identity Verification, Financial Aid and Ability to Pay
    }

    tc = {
        'subscriber': subscriber_info,
        'queryType': 'CR'
    }
    return tc


def _get_product(applicant):
    """
    the <product> element contains a series of elements that identify the
    subject to use for this request
    """
    product = {
        'subject': {
            'subjectRecord': {
                'indicative': {
                    'name': _get_name(applicant),
                    'address': _get_address(applicant),
                    'socialSecurity': _get_ssn(applicant['ssn']),
                    'dateOfBirth': _get_dob(applicant['birthdate'])
                }
            }
        }
    }

    return product


def _get_name(applicant):
    """
    The <person> element is nested in the <name> element and contains fields
    that identify the subject in the request.
    """
    person = {
        'person': {
            'first': applicant['first_name'],
            'last': applicant['last_name']
        }
    }
    mid_name = applicant.get('middle_name')
    if mid_name:
        person['person']['middle'] = mid_name
    return person


def _get_address(applicant):
    address = {
        'street': {
            'unparsed': applicant['address']
        },
        'location': {
            'city': applicant['city'],
            'state': applicant['state'],
            'zipCode': applicant['postal_code'][:5]
        }
    }
    return address


def _get_ssn(ssn):
    return {'number': ssn.replace('-', '')}


def _get_dob(dob):
    return str(dob)
