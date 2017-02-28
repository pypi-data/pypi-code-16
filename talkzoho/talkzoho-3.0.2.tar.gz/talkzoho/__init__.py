import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


from .books.books_client import BooksClient  # noqa
from .crm.crm_client import CRMClient  # noqa
from .projects.projects_client import ProjectsClient  # noqa
from .support.support_client import SupportClient  # noqa