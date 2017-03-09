import json
import copy

from fara_principals.exceptions import (
    InvalidPrincipalError, InvalidExhibitError
)

class ForeignPrincipal:

    def __init__(self, url=None, country=None, state=None, address=None, 
        reg_number=None, principal_name=None, principal_reg_date=None, 
        reg_date=None, registrant=None, exhibits=[], partial_dict=None, 
        *args, **kwargs):

        self._dict_info = None
        if partial_dict:
            self._dict_info = partial_dict
        else:
            self._dict_info = {
                "url": url, "country": country, "state": state, 
                "address": address, "reg_number": reg_number, 
                "principal_name": principal_name, 
                "principal_reg_date": principal_reg_date, 
                "reg_date": reg_date, "registrant": registrant,
                "exhibits": exhibits
            }


        self._required_keys = ["url", "country", "state", "address", 
        "reg_number", "principal_name", "principal_reg_date", "reg_date"]

    def validate_data(self):
        """
        Confirms that certain keys are present in the dict returned by 
        `self.to_dict`

        Raises:
            InvalidPrincipalError: raised when certain fields(keys) are 
            unavailable or when required contrains on the schema are not met.

        Note: this method is to be called when it has been populated with 
        it's exhibit info.
        """
        self.validate_partial()
        key = "exhibit"
        try:
            self.to_dict()[key]
        except KeyError:
            raise InvalidPrincipalError("key `{}` not present".format(key))

    def validate_partial(self):
        """
        Confirms that certain keys are present given that this instance 
        represents a pricipal whose full data has not yet been collected.

        Raises:
            BadPrincipalSchemaError: raised when certain fields(keys) are 
            unavailable or when required contrains on the schema are not met.
        """
        for key in self._required_keys:
            try:
                self.to_dict()[key]
            except KeyError:
                raise InvalidPrincipalError(
                    "key `{}` not present".format(key))

        #todo: create more flexible implementation for this
        if not self.to_dict()["principal_name"]:
            raise InvalidPrincipalError(
                "required field `{}` is empty".format("principal_name"))
        if not self.to_dict()["reg_number"]:
            raise InvalidPrincipalError(
                "required field `{}` is empty".format("reg_number"))
        if not self.to_dict()["country"]:
            raise InvalidPrincipalError(
                "required field `{}` is empty".format("country"))
        if not self.to_dict()["principal_reg_date"]:
            raise InvalidPrincipalError(
                "required field `{}` is empty".format("principal_reg_date"))

    def is_partial(self):
        """
        Returns:
            bool: True if the principal this instance represents does not
            yet contain all it's information including it's exibit data.

        Note: a principal is usually still partial when it has been 
        populate from the list page but not from its detail page.
        """
        return self.to_dict().get("exhibit") == None

    def to_dict(self):
        """
        Returns:
            dict: a dict representation of the Principal instance
        """
        return copy.deepcopy(self._dict_info)

    def to_json(self):
        """
        Returns:
            str: a json string representation of the Principal instance
        """
        return json.dumps(self.to_dict())

    def add_exhibit_dict(self, exhibit):
        """
        Args:
            exhibit(dict): dict containing exhibit info
        """
        if not self._dict_info.get("exhibit"):
            self._dict_info["exhibit"] = [exhibit]
        else:
            self._dict_info["exhibit"].append(exhibit)

class Exhibit:
    """
    Exhibit class which provides validation utillities for exhibit data
    for a Principal
    """
    def __init__(self, exhibit_dict, *args, **kwargs):
        self._exhibit_dict = exhibit_dict

    def to_dict(self):
        return copy.deepcopy(self._exhibit_dict)

    def validate(self):
        required_exhibit_fields = [
            "date_stamped", "document_link", "reg_number", "registrant",
            "document_type"
        ]

        for key in required_exhibit_fields:
            try:
                self._exhibit_dict[key]
            except KeyError:
                raise InvalidExhibitError(
                    "key `{}` not found in exhibit".format(key))