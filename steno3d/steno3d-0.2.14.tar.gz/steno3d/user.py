"""user.py contains basic information about the steno3d user"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .traits import HasSteno3DTraits, Int, String


class User(HasSteno3DTraits):
    """Class representing a user instance"""
    _model_api_location = "user"

    email = String(
        help='Email',
        default_value=None,
        allow_none=True,
        read_only=True
    )
    name = String(
        help='Name',
        default_value=None,
        allow_none=True,
        read_only=True
    )
    url = String(
        help='URL',
        default_value=None,
        allow_none=True,
        read_only=True
    )
    affiliation = String(
        help='Affiliation',
        default_value=None,
        allow_none=True,
        read_only=True
    )
    location = String(
        help='Location',
        default_value=None,
        allow_none=True,
        read_only=True
    )
    username = String(
        help='Username',
        default_value=None,
        allow_none=True,
        read_only=True
    )

    devel_key = String(
        help='Developer API Key',
        default_value=None,
        allow_none=True,
        read_only=True
    )

    file_size_limit = Int(
        help='Inidividual file limit',
        default_value=5000000,
        read_only=True
    )
    project_size_limit = Int(
        help='Project size limit',
        default_value=25000000,
        read_only=True
    )
    project_resource_limit = Int(
        help='Maximum resources in a project',
        default_value=25,
        read_only=True
    )

    def login_with_json(self, login_json):
        self.set_trait('username', login_json['uid'])
        self.set_trait('email', login_json['email'])
        self.set_trait('name', login_json['name'])
        self.set_trait('url', login_json['url'])
        self.set_trait('affiliation', login_json['affiliation'])
        self.set_trait('location', login_json['location'])

    def set_key(self, devel_key):
        self.set_trait('devel_key', devel_key)

    def logout(self):
        self.set_trait('username', None)
        self.set_trait('email', None)
        self.set_trait('name', None)
        self.set_trait('url', None)
        self.set_trait('affiliation', None)
        self.set_trait('location', None)
        self.set_trait('devel_key', None)

    @property
    def logged_in(self):
        return self.username is not None
