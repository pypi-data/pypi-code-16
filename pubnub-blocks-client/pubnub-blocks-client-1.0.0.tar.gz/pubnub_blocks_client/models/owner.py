"""PubNub account owner representation module."""
from pubnub_blocks_client.models.model import Model


class Owner(Model):
    """PubNub account owner representation model."""

    def __init__(self, user_data):
        """Construct account owner model.

        Model used to provide available personal information about account
        owner.
        :type user_data:  dict
        :param user_data: Reference on dictionary which contain information
                          which can be used to fill up required model
                          fields.

        :rtype:  Owner
        :return: Initialized account owner model.
        """
        super(Owner, self).__init__(user_data)

    @property
    def uid(self):
        """Stores reference on unique account owner identifier.

        :rtype:  int
        :return: Reference on unique user account identifier.
        """
        return self.get_property('user.id', is_path=True)

    @property
    def creation_date(self):
        """Stores reference on account creation date.

        Date stored in unix-timestamp format.
        :rtype:  int
        :return: Reference on account owner name.
        """
        return self.get_property('user.properties.created', is_path=True)

    @property
    def first_name(self):
        """Stores reference on account owner first name

        :rtype:  str | None
        :return: Reference on account owner first name. 'None' in case if
                 value not provided.
        """
        return self.get_property('user.properties.first', is_path=True)

    @property
    def last_name(self):
        """Stores reference on account owner last name

        :rtype:  str | None
        :return: Reference on account owner last name. 'None' in case if
                 value not provided.
        """
        return self.get_property('user.properties.last', is_path=True)

    @property
    def phone(self):
        """Stores reference on account owner first name

        :rtype:  int
        :return: Reference on account owner contact number.
        """
        return self.get_property('user.properties.phone', is_path=True)

    @property
    def email(self):
        """Stores reference on account owner first name

        :rtype:  str
        :return: Reference on account owner contact email.
        """
        return self.get_property('user.email', is_path=True)

    @property
    def twitter(self):
        """Stores reference on account owner first name

        :rtype:  str | None
        :return: Reference on account owner twitter name.
        """
        return self.get_property('user.properties.twitter', is_path=True)
