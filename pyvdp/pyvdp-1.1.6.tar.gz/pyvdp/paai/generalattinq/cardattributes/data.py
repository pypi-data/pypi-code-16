class GeneralInquiryData(object):
    """General Card Attributes Inquiry data object model.

    :param str pan: **Required**. Primary account number (PAN). 13-19 characters string.

    **Example:**
        ..  code-block:: json

            {
                "primaryAccountNumber": "4465390000029077"
            }
    """
    ATTR_MAPPINGS = {
        'pan': 'primaryAccountNumber'
    }

    def __init__(self, **kwargs):
        self.__dict__.update((self.ATTR_MAPPINGS[k], v) for k, v in kwargs.items() if k in self.ATTR_MAPPINGS and v)
