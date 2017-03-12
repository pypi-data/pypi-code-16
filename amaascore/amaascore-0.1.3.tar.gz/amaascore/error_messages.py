# TODO - Support multi-language errors
ERROR_LOOKUP = {'address_invalid': 'Invalid addresses attribute: %s. Party ID %s for Asset Manager %s',
                'address_primary': 'Must set exactly one address as primary. Party ID %s for Asset Manager %s',
                'email_invalid': 'Invalid emails attribute: %s. Party ID %s for Asset Manager %s',
                'email_primary': 'Must set exactly one email as primary. Party ID %s for Asset Manager %s',
                'email_address_invalid': 'Invalid email(s): %s. Party ID %s for Asset Manager %s',
                'amend_missing_previous': 'Cannot find party to amend: ID %s for Asset Manager %s',
                'amend_missing_attribute': 'Partial amend failed for Asset Manager: %s on party: %s - '
                                           'Attribute: %s does not exist',
                'deactivate_missing_previous': 'Cannot Deactivate Party - Cannot Find ID: %s for Asset Manager: %s',
                'party_status_invalid': 'Invalid party status %s. Party ID: %s for Asset Manager: %s',
                'transaction_action_invalid': 'Invalid transaction action %s. Transaction ID: %s for Asset Manager: %s',
                'transaction_status_invalid': 'Invalid transaction status %s. Transaction ID: %s for Asset Manager: %s',
                'transaction_type_invalid': 'Invalid transaction type %s. Transaction ID: %s for Asset Manager: %s',
                'transaction_link_not_found': 'Cannot remove link - not found'}
