import re

import six

post = ["SW1W 0NY", "PO16 7GZ", "GU16 7HF", "L1 8JQ"]

class Uk:
    @classmethod
    def validate(cls, code):
        """
        Check the validity of postal code
        """
        if isinstance(code, six.binary_type):
            code = str(code, "utf-8") if six.PY3 else code.decode("utf-8")
        if not isinstance(code, six.string_types):
            raise ValueError("expected  string or bytes-like object but got a '%s' " % code.__class__.__name__)

        valid = False
        code = code.lower()
        if cls.check_postal_code(code):
            outwardcode, inwardcode = code.split(" ")
            if cls.check_outward_code(outwardcode) and cls.check_inward_code(inwardcode):
                valid = True

        return valid

    @classmethod
    def check_postal_code(cls, postcode):
        """
        Checks the basic structure of the code.

        checks the following patterns pass:
            - AA9A 9AA
            - A9A 9AA
            - A9 9AA
            - A99 9AA
            - AA9 9AA
            - AA99 9AA

        """
        return True if re.match("[a-z]{1,2}[0-9][0-9a-z]?\s{1}[0-9][a-z]{2}", postcode) else False

    @classmethod
    def check_outward_code(cls, outwardcode):
        """
        Check the validity of postal code - outward code section.

        code is a valid outward code if:
             - has two and four characters long
             - The letters QVX are not used in the first position.
             - The letters IJZ are not used in the second position.
             - The only letters to appear in the third position are ABCDEFGHJKPSTUW when the structure starts with A9A.
             - The only letters to appear in the fourth position are ABEHMNPRVWXY when the structure starts with AA9A.

        :return True|False

        """
        # The letters QVX are not used in the first position
        if re.match("^[a-pr-uwyz]", outwardcode):

            # check the A9A structure
            # must fullfill 3rd position requirement
            if re.match("^[a-z][0-9][a-z]", outwardcode):
                return True if re.match("^[a-pr-uwyz][0-9][abcdefghjkpstuw]", outwardcode) else False

            # check the 2nd position for AA9 structure
            if re.match("^[a-z]{2}[0-9]", outwardcode):

                # check the AA9A structure 4th position
                if re.match("^[a-z]{2}[0-9][a-z]", outwardcode):
                    # must fullfill 2nd position and 4th position requirements
                    return True if re.match("^[a-pr-uwyz][a-hl-y][0-9][abehmnprvwxy]", outwardcode) else False

                # must fullfill 2nd position requirement
                if re.match("^[a-pr-uwyz][a-hl-y]", outwardcode):
                    return True
                else:
                    return False

            # takes care of A9 structure
            return True

        return False

    @classmethod
    def check_inward_code(cls, inwardcode):
        """
        Check the validity of postal code - inward code section.

        valid if :
            - must start with a digit followed by two letters
            - the letters don't use CIKMOV.

        :return True|False

        """
        return True if re.match("[0-9][abd-hjlnp-uw-z]{2}", inwardcode) else False

