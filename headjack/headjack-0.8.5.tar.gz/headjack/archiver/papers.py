#!/usr/local/bin/python
# encoding: utf-8
"""
*opinionated importer for macOS Papers.app*

:Author:
    David Young

:Date Created:
    March 11, 2017

Usage:
    papers [-d] add <pdfPath>

Options:
    add                   import into papers.app

    <pdfPath>             the path to the PDF file

    -d, --delete          delete the original file after import
    -h, --help            show this help message
    -v, --version         show version
    -s, --settings        the settings file

"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import docopt
from fundamentals import tools, times


def main(arguments=None):
    """
    The main function used when ``papers.py`` is run as a single script from the cl, or when installed as a cl command
    """

    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="WARNING",
        options_first=False
    )
    arguments, settings, log, dbConn = su.setup()

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    if add:
        p = papers(
            log=log,
            settings=settings
        )
        p.archive(
            pdfPath=pdfPath,
            delete=deleteFlag
        )

    return


class papers():
    """
    *papers.app object*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**

        To setup your logger, settings and database connections, please use the ``fundamentals`` package (`see tutorial here <http://fundamentals.readthedocs.io/en/latest/#tutorial>`_). 

        To initiate a papers object, use the following:

        .. code-block:: python 

            from headjack.archiver import papers as p
            papers = p(
                log=log,
                settings=settings
            )  
    """
    # Initialisation

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'papers' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # Initial Actions

        return None

    def archive(self, pdfPath, delete=False):
        """
        *import a PDF (or any media file) into papers and give the title as the filename of the PDF*

        **Key Arguments:**
            - ``pdfPath`` -- the path to the PDF to import
            - ``delete`` -- delete the original file after successful import. Default *False*

        **Return:**
            - ``success`` -- -1 for fail 1 for success

        **Usage:**

            .. todo:: 

                - create cl-util for this method
                - update the package tutorial if needed

            To import the PDF file ``a_lovely_detailed_title.pdf`` into papers with the title 'a lovely detailed title' and then delete the original file, run:

            .. code-block:: python 

                from headjack.archiver import papers as p
                papers = p(
                    log=log,
                    settings=settings
                )  
                papers.archive(
                    pdfPath="/path/to/my/a_lovely_detailed_title.pdf",
                    delete=True
                )
        """
        self.log.info('starting the ``archive`` method')

        title = os.path.basename(pdfPath)
        title = os.path.splitext(title)[0].replace("_", " ").strip()

        from subprocess import Popen, PIPE, STDOUT
        applescript = """
            tell application "Papers"
                activate
                open POSIX file "%(pdfPath)s"
                set oneHrAgo to (current date) - (60 * 60)
                set theseItems to publication items whose import date comes after oneHrAgo
                
                set the index_list to {}
                set the sorted_list to {}
                repeat (the number of items in theseItems) times
                    set the high_item to ""
                    repeat with i from 1 to (number of items in theseItems)
                        if i is not in the index_list then
                            set this_item to item i of theseItems
                            if the high_item is "" then
                                set the high_item to this_item
                                set the high_item_index to i
                            else if import date of this_item comes after the import date of high_item then
                                set the high_item to this_item
                                set the high_item_index to i
                            end if
                        end if
                    end repeat
                    set the end of sorted_list to the high_item
                    set the end of the index_list to the high_item_index
                end repeat
                
                set thisItem to first item in sorted_list
                set title of thisItem to "%(title)s"
                return "all ok"
            end tell
        """ % locals()
        cmd = "\n".join(["osascript << EOT", applescript, "EOT"])
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        self.log.debug('output: %(stdout)s' % locals())

        if "all ok" in stdout and len(stderr) == 0:
            if delete:
                os.remove(pdfPath)
            success = 1
        if len(stderr) > 0:
            self.log.error(stderr)
            success = -1

        self.log.info('completed the ``archive`` method')
        return success

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx


if __name__ == '__main__':
    main()
