from __future__ import absolute_import, unicode_literals

import os

from ..compat import MAYAN_VERSION

TEST_CABINET_LABEL = 'test cabinet label'
TEST_CABINET_EDITED_LABEL = 'test cabinet edited label'

if MAYAN_VERSION[0:2] <= (2, 1):
    TEST_SMALL_DOCUMENT_FILENAME = 'title_page.png'

    TEST_SMALL_DOCUMENT_PATH = os.path.join(
        'contrib', 'sample_documents',
        TEST_SMALL_DOCUMENT_FILENAME
    )
else:
    from documents.tests import TEST_SMALL_DOCUMENT_PATH  # NOQA
