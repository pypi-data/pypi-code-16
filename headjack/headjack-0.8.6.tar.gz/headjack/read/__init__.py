"""
*all of the reading related tools*
"""

from sendToKindle import sendToKindle
from fundamentals.files import recursive_directory_listing
from convertKindleNB import convertKindleNB
from generate_web_article_epubs import generate_web_article_epubs


def get_pdf_paths(
        log,
        settings):
    """*generate a dictionary of pdf-names and their paths*

    **Key Arguments:**
        - ``log`` -- the logger

    **Return:**
        - ``pdfDict`` -- the dictionary of pdf paths (keys are pdf names)

    **Usage:**

        To generate a list of dictionaries of ``{pdfName: pdfPath}`` for PDFs in the reading-list folder, use the code:

        .. code-block:: python

            from headjack.read import get_pdf_paths
            pdfDict = get_pdf_paths(
                log=log,
                settings=settings)
            print pdfDict
    """
    import os
    log.info('starting the ``get_pdf_paths`` method')

    fileList = recursive_directory_listing(
        log=log,
        baseFolderPath=settings["read"]["reading_list_root_path"],
        whatToList="files"  # all | files | dirs
    )
    pdfDict = {}
    for f in fileList:
        if f.split(".")[-1].lower() == "pdf":
            pdfDict[os.path.basename(f)] = f

    log.info('completed the ``get_pdf_paths`` method')
    return pdfDict
