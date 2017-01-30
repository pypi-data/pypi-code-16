"""A Henson plugin to interact with S3."""

import os as _os
import pkg_resources as _pkg_resources

from boto3.session import Session
from botocore.exceptions import ClientError
from henson import Extension

__all__ = ('S3',)

try:
    _dist = _pkg_resources.get_distribution(__name__)
    if not __file__.startswith(_os.path.join(_dist.location, __name__)):
        # Manually raise the exception if there is a distribution but
        # it's installed from elsewhere.
        raise _pkg_resources.DistributionNotFound
except _pkg_resources.DistributionNotFound:
    __version__ = 'development'
else:
    __version__ = _dist.version


class S3(Extension):
    """A class to interact with S3."""

    DEFAULT_SETTINGS = {
        'AWS_ACCESS_KEY_ID': None,
        'AWS_SECRET_ACCESS_KEY': None,
        'AWS_BUCKET_NAME': None,
        'AWS_REGION_NAME': None,
    }

    def init_app(self, app):
        """Initialize an ``Application`` instance.

        Args:
            app (henson.base.Application): The application instance to
                be initialized.
        """
        super().init_app(app)

        self._session = Session(
            aws_access_key_id=app.settings['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.settings['AWS_SECRET_ACCESS_KEY'],
            region_name=app.settings['AWS_REGION_NAME'],
        )
        app.startup(self._connect)

    async def check(self, key, *, bucket=None):
        """Check to see if a file exists in an S3 bucket.

        Args:
            key (str): The name of the file for which to check.
            bucket (~typing.Optional[str]): THe name of the bucket in
                which to check for the file. If no value is provided,
                the ``AWS_BUCKET_NAME`` setting will be used.

        Returns:
            bool: True if the file exists.

        Raises:
            ValueError: If no bucket name is specified.
        """
        bucket = bucket or self.app.settings['AWS_BUCKET_NAME']
        if not bucket:
            raise ValueError('A bucket name is required.')

        try:
            self._client.head_object(Bucket=bucket, Key=key)
        except ClientError:
            return False
        else:
            return True

    async def download(self, key, *, bucket=None):
        """Return the contents of a file in an S3 bucket.

        Args:
            key (str): The name of the file to download.
            bucket (~typing.Optional[str]): The name of the bucket from
                which to download the file. If no value is provided, the
                ``AWS_BUCKET_NAME`` setting will be used.

        Returns:
            bytes: The contents of the file.

        Raises:
            FileNotFoundError: If the key isn't found.
            ValueError: If no bucket name is specified.
        """
        bucket = bucket or self.app.settings['AWS_BUCKET_NAME']
        if not bucket:
            raise ValueError('A bucket name is required.')

        try:
            file = self._client.get_object(Bucket=bucket, Key=key)
        except ClientError:
            raise FileNotFoundError("'{}' was not found in '{}'".format(
                key, bucket))

        return file['Body'].read()

    # TODO: Support other S3 settings (e.g., ACL, CacheControl).
    async def upload(self, key, file, *, bucket=None):
        """Upload a file to an S3 bucket.

        Args:
            key (str): The name of the file to upload.
            file (bytes): The contents of the file.
            bucket (~typing.Optional[str]): The name of the bucket to
                which to upload the file. If no value is provided, the
                ``AWS_BUCKET_NAME`` setting will be used.

        Raises:
            ValueError: If no bucket name is specified.
        """
        bucket = bucket or self.app.settings['AWS_BUCKET_NAME']
        if not bucket:
            raise ValueError('A bucket name is required.')

        self._client.put_object(Body=file, Bucket=bucket, Key=key)

    async def _connect(self, app):
        """Create an S3 client.

        Args:
            app (henson.base.Application): The application instance
                against which to register the client.
        """
        self._client = self._session.client('s3')
