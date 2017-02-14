"""
CONFIGURATION

Class based config file, where each class is an environment:
ie: Dev = Development, Prod=Production, ...

Shaft: Global Configuration

Global config shared by all applications

The method allow multiple configuration

By default, it is expecting the Dev and Prod, but you can add your class
which extends from BaseConfig
"""

from . import (get_var_path,
               ROOT_DIR,
               VAR_DIR,
               AVAILABLE_APPS)


class BaseConfig(object):
    """
    Base Configuration.
    """

# ------------------------------------------------------------------------------
#: APPLICATION_*
    # Your own application variable that will not affect Shaft at all
    # But holds a trick of exposing the data into the template global variables
    # ie: APPLICATION_NAME can be accessed in your template as __.APPLICATION_NAME
    # APPLICATION_GOOGLE_ANALYTICS_ID -> __.APPLICATION_GOOGLE_ANALYTICS_ID
    #

    #: Site's name or Name of the application
    APPLICATION_NAME = "Shaft"

    #: The application url
    APPLICATION_URL = ""

    #: Version of application
    APPLICATION_VERSION = "0.0.1"

    #: Google analytics
    APPLICATION_GOOGLE_ANALYTICS_ID = ""

    # Application global vars
    APPLICATION_VARS = {

    }

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#: MISC CONFIG

    #: Required to setup. This email will have SUPER USER role
    ADMIN_EMAIL = None

    #: The address to receive email when using the contact page
    CONTACT_EMAIL = None

    #: PAGINATION_PER_PAGE : Total entries to display per page
    PAGINATION_PER_PAGE = 20

    # MAX_CONTENT_LENGTH
    # If set to a value in bytes, Flask will reject incoming requests with a
    # content length greater than this by returning a 413 status code
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # To remove whitespace off the HTML result
    COMPRESS_HTML = False

# ------------------------------------------------------------------------------
#: DATETIME TIMEZONE + FORMAT

    # Timezone
    DATETIME_TIMEZONE = "US/Eastern"

    # The date format. Will be used in the jinja `date` extension -> {{ my_date_time | local_date }}
    DATETIME_DATE_FORMAT = "MM/DD/YYYY"

    # The date format. Will be used in the jinja `date_time` extension -> {{ my_date_time | local_date_time }}
    DATETIME_DATETIME_FORMAT = "MM/DD/YYYY hh:mm"

    # Time format
    DATETIME_TIME_FORMAT = "hh:mm"

# ------------------------------------------------------------------------------
#: AWS CREDENTIALS

    #: AWS Credentials
    # AWS is used by lots of extensions
    # For: S3, SES Mailer, flask S3.

    # The AWS Access KEY
    AWS_ACCESS_KEY_ID = ""

    # Secret Key
    AWS_SECRET_ACCESS_KEY = ""

    # The bucket name for S3
    AWS_S3_BUCKET_NAME = ""

    # The default region name
    AWS_REGION_NAME = "us-east-1"

# ------------------------------------------------------------------------------
#: DATABASES

    #: DB_URI
    #: format: engine://USERNAME:PASSWORD@HOST:PORT/DB_NAME
    DB_URI = "sqlite:////%s/db.db" % VAR_DIR

    #: REDIS_URI
    #: format: USERNAME:PASSWORD@HOST:PORT
    REDIS_URI = None

# ------------------------------------------------------------------------------
#: ASSETS DELIVERY

    # ASSETS DELIVERY allows to serve static files from S3, Cloudfront or other CDN

    # The delivery method:
    #   - None: will use the local static files
    #   - S3: Will use AWS S3. By default it will use the bucket name set in AWS_S3_BUCKET_NAME
    #       When S3, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required to upload files
    #   - CDN: To use a CDN. ASSETS_DELIVERY_DOMAIN need to have the CDN domain
    ASSETS_DELIVERY_METHOD = None

    # Set the base domain of the CDN
    ASSETS_DELIVERY_DOMAIN = None


# ------------------------------------------------------------------------------
#: SESSION

    #: SESSION
    #: Flask-KVSession is used to save the user's session
    #: Set the SESSION_URI by using these examples below to set KVSession
    #: To use local session, just set SESSION_URI to None
    #:
    #: Redis: redis://username:password@host:6379/db
    #: S3: s3://username:password@s3.aws.amazon.com/bucket
    #: Google Storage: google_storage://username:password@cloud.google.com/bucket
    #: SQL: postgresql://username:password@host:3306/db
    #:      mysql+pysql://username:password@host:3306/db
    #:      sqlite://
    #: Memcached: memcache://host:port
    #:
    SESSION_URI = None

# ------------------------------------------------------------------------------
#: STORAGE

    #: STORAGE
    #: Flask-Cloudy is used to save upload on S3, Google Storage,
    #: Cloudfiles, Azure Blobs, and Local storage
    #: When using local storage, they can be accessed via http://yoursite/files
    #:

    #: STORAGE_PROVIDER:
    # The provider to use. By default it's 'LOCAL'.
    # You can use:
    # LOCAL, S3, GOOGLE_STORAGE, AZURE_BLOBS, CLOUDFILES
    STORAGE_PROVIDER = "LOCAL"

    #: STORAGE_KEY
    # The storage key. Leave it blank if PROVIDER is LOCAL
    STORAGE_KEY = AWS_ACCESS_KEY_ID

    #: STORAGE_SECRET
    #: The storage secret key. Leave it blank if PROVIDER is LOCAL
    STORAGE_SECRET = AWS_SECRET_ACCESS_KEY

    #: STORAGE_REGION_NAME
    #: The region for the storage. Leave it blank if PROVIDER is LOCAL
    STORAGE_REGION_NAME = AWS_REGION_NAME

    #: STORAGE_CONTAINER
    #: The Bucket name (for S3, Google storage, Azure, cloudfile)
    #: or the directory name (LOCAL) to access
    STORAGE_CONTAINER = get_var_path("uploads")

    #: STORAGE_SERVER
    #: Bool, to serve local file
    STORAGE_SERVER = True

    #: STORAGE_SERVER_URL
    #: The url suffix for local storage
    STORAGE_SERVER_URL = "files"

# ------------------------------------------------------------------------------
#: MAIL

    # AWS SES
    # To use AWS SES to send email
    #:
    #: - To use the default AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    #: set MAIL_URI = "ses://"
    #: * To use a different credential:
    #: set MAIL_URI = "ses://{access_key}:{secret_key}@{region}"
    #:
    #: *** uncomment if you are using SMTP instead
    # MAIL_URI = "ses://"

    # SMTP
    #: If you are using SMTP, it will use Flask-Mail
    #: The uri for the smtp connection. It will use Flask-Mail
    #: format: smtp://USERNAME:PASSWORD@HOST:PORT
    #: with sll -> smtp+ssl://USERNAME:PASSWORD@HOST:PORT
    #: with ssl and tls -> smtp+ssl+tls://USERNAME:PASSWORD@HOST:PORT
    #:
    #: *** comment out if you are using SES instead
    # MAIL_URI = "smtp+ssl://{username}:{password}@{host}:{port}"\
    #    .format(username="", password="", host="smtp.gmail.com", port=465)

    #: MAIL_SENDER - The sender of the email by default
    #: For SES, this email must be authorized
    MAIL_SENDER = ADMIN_EMAIL

    #: MAIL_REPLY_TO
    #: The email to reply to by default
    MAIL_REPLY_TO = ADMIN_EMAIL

    #: MAIL_TEMPLATE
    #: a directory that contains the email template or a dict
    MAIL_TEMPLATE = get_var_path("mail-templates")

    #: MAIL_TEMPLATE_CONTEXT
    #: a dict of all context to pass to the email by default
    MAIL_TEMPLATE_CONTEXT = {
        "params": {
            "site_name": APPLICATION_NAME,
            "site_url": APPLICATION_URL
        }
    }

# ------------------------------------------------------------------------------
#: CACHE

    #: Flask-Cache is used to caching

    #: CACHE_TYPE
    #: The type of cache to use
    #: null, simple, redis, filesystem,
    CACHE_TYPE = "simple"

    #: CACHE_REDIS_URL
    #: If CHACHE_TYPE is 'redis', set the redis uri
    #: redis://username:password@host:port/db
    CACHE_REDIS_URL = ""

    #: CACHE_DIR
    #: Directory to store cache if CACHE_TYPE is filesystem, it will
    CACHE_DIR = ""

# ------------------------------------------------------------------------------
#: RECAPTCHA

    #: Flask-Recaptcha
    #: Register your application at https://www.google.com/recaptcha/admin

    #: RECAPTCHA_ENABLED
    RECAPTCHA_ENABLED = False

    #: RECAPTCHA_SITE_KEY
    RECAPTCHA_SITE_KEY = ""

    #: RECAPTCHA_SECRET_KEY
    RECAPTCHA_SECRET_KEY = ""


# ------------------------------------------------------------------------------
#: INSTALLED_APPS
    #
    # Installed apps/extensions to your application
    # The order is important. If an app depends on another app to work
    # that must be placed before the calling app
    #
    INSTALLED_APPS = [
        AVAILABLE_APPS["ERROR_PAGE"]
    ]

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# --- ENVIRONMENT BASED CONFIG -------------------------------------------------


class Dev(BaseConfig):
    """
    Config for development environment
    """
    SERVER_NAME = None
    DEBUG = True
    SECRET_KEY = "PLEASE CHANGE ME"


class Prod(BaseConfig):
    """
    Config for Production environment
    """
    SERVER_NAME = None
    DEBUG = False
    SECRET_KEY = None
    COMPRESS_HTML = True
