from amaascore.core.amaas_model import AMaaSModel


class Address(AMaaSModel):

    def __init__(self, line_one, city, country_id, address_primary, line_two=None, region=None, postal_code=None,
                 active=True, version=1, *args, **kwargs):
        self.address_primary = address_primary
        self.line_one = line_one
        self.line_two = line_two
        self.city = city
        self.region = region
        self.postal_code = postal_code
        self.country_id = country_id
        self.active = active
        self.version = version
        super(Address, self).__init__(*args, **kwargs)


class Email(AMaaSModel):

    def __init__(self, email, email_primary, active=True, version=1, *args, **kwargs):
        self.email_primary = email_primary
        self.email = email
        self.active = active
        self.version = version
        super(Email, self).__init__(*args, **kwargs)
