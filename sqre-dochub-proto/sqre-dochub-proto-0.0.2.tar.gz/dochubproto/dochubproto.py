#!/usr/bin/env python
"""DocHubProto provides a class to generate the www.lsst.io index page.
"""
import os
import sys
import time
from threading import Thread, Lock
import jinja2
import requests
import yaml
from apikit import get_logger, raise_from_response, retry_request, BackendError
from .sections import SECTIONS

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class DocHubProto(object):
    """A DocHubProto object represents the DocHub prototype.  It comes with
    a number of methods to check the object state and to retrieve data.

    The state will be one of STATE_EMPTY, STATE_READY, STATE_REFRESHING,
    or STATE_STALE, which map to the strings "empty", "ready", "refreshing",
    or "stale", respectively.

    The document data will be returned as a dict indexed by document section
    (e.g. "DMTN") and then, within that section, as a list ordered by
    document handle (e.g. "dmtn-038").

    Rendered document data will be returned as an HTML unordered list entity.

    State can be checked with check_state().

    Data retrieval methods are: get_document_data() and
    get_fresh_document_data().  The second one checks freshness and refreshes
    if the data is stale before returning the data.

    HTML-rendered data can be retrieved with render(); this can take a
    refresh_if_stale boolean, which will check data freshness and refresh
    if necessary before returning rendered data.  It returns an HTML ul
    entity.

    A complete HTML index page can be retrieved with render_index().  It
    calls render() and takes the same refresh_if_stale boolean.  It returns
    an HTML document.

    The two methods refresh_document_data() and start_refresh_document_data()
    get fresh data from the backend data sources.  The first is synchronous,
    and the second returns immediately (you can poll check_state() to determine
    when refresh has completed).

    Finally, the methods debug(), info(), warning(), error(), and critical()
    log messages at the specified level via an apikit-provided structured
    data logger.
    """

    # pylint: disable = too-many-instance-attributes
    DEFAULT_KEEPER_URL = "https://keeper.lsst.codes"
    DEFAULT_MAX_DOCUMENT_DATA_AGE = 3600.0
    DEFAULT_UL_TEMPLATE_NAME = "doclist.jinja2"
    DEFAULT_IDX_TEMPLATE_NAME = "index.jinja2"
    STATE_EMPTY = "empty"
    STATE_READY = "ready"
    STATE_REFRESHING = "refreshing"
    STATE_STALE = "stale"

    def __init__(self):
        """Create a DocHubProto object.

        It uses the following environment variables: KEEPER_URL, LOGLEVEL,
        TEMPLATE_DIR, UL_TEMPLATE_NAME, IDX_TEMPLATE_NAME, and
        MAX_DOCUMENT_DATA_AGE.  If those are not specified, the default values
        are, respectively, "https://keeper.lsst.codes", "WARNING", "templates"
        relative to the dochubproto module, "doclist.jinja2", "index.jinja2",
        and "3600" (age is expressed in seconds and must be convertible to a
        Python float).
        """
        name = 'dochubproto'
        self.keeper_url = os.getenv("KEEPER_URL", self.DEFAULT_KEEPER_URL)
        loglevel = os.getenv("LOGLEVEL")
        self.logger = get_logger(level=loglevel)
        self.document_data = None
        self.template_dir = os.getenv("TEMPLATE_DIR")
        # pylint: disable=bad-continuation
        if not self.template_dir:
            self.template_dir = os.path.dirname(sys.modules[name].__file__
                                                ) + "/templates"
        self.info("TD %s" % self.template_dir)
        self.ul_template_name = os.getenv(
            "UL_TEMPLATE_NAME", self.DEFAULT_UL_TEMPLATE_NAME)
        self.idx_template_name = os.getenv(
            "IDX_TEMPLATE_NAME", self.DEFAULT_IDX_TEMPLATE_NAME)
        self.jinja_loader = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
        self.ul_renderer = self.jinja_loader.get_template(
            self.ul_template_name)
        self.idx_renderer = self.jinja_loader.get_template(
            self.idx_template_name)
        self.max_document_data_age = self.DEFAULT_MAX_DOCUMENT_DATA_AGE
        mdda = "MAX_DOCUMENT_DATA_AGE"
        mca = os.getenv(mdda)
        if mca:
            try:
                self.max_document_data_age = float(mca)
            except ValueError:
                self.warning("Could not convert %s '%s' to number" %
                             (mdda, mca))
        self.document_refresh_time = 0.0  # The epoch stands in for "never"
        self.state = "empty"

    def debug(self, *args, **kwargs):
        """Log debug-level message.
        """
        if self.logger:
            self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        """Log info-level message.
        """
        if self.logger:
            self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """Log warning-level message.
        """
        if self.logger:
            self.logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Log error-level message.
        """
        if self.logger:
            self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        """Log critical-level message.
        """
        if self.logger:
            self.logger.critical(*args, **kwargs)

    def start_document_data_refresh(self):
        """Start document data refresh in a separate thread, and return
        immediately.  Progress can be monitored by polling with the
        check_status() method.
        """
        thd = Thread(target=self.refresh_document_data)
        thd.start()
        # Thread will exit when function returns; no need to manually join()
        return

    def refresh_document_data(self):
        """Refresh the document data.
        """
        # pylint: disable=too-many-branches
        docurls = self._get_docurls()
        count = 0
        mutex = Lock()
        mutex.acquire()
        try:
            if self.state == self.STATE_REFRESHING:
                self.info("Refresh is already in progress.")
                count = 1
                while self.state == self.STATE_REFRESHING:
                    # Wait until the refresh finishes
                    self.debug("Waiting ten seconds for refresh (#%d)" % count)
                    count += 1
                    time.sleep(10)
                self.info("Refresh complete.")
            else:
                docdata = []
                self.state = self.STATE_REFRESHING
        finally:
            mutex.release()
        if count > 0:
            # We waited for another one to run, so we're fresh.
            return
        tthreads = []
        for keeperurl in docurls:
            thd = Thread(target=self._get_keeper_data,
                         args=(keeperurl, mutex, docdata))
            tthreads.append(thd)
            thd.start()
        # Here, we must wait for all the threads to complete, so that
        #  we have all the data assembled before we modify document_data.
        for thd in tthreads:
            thd.join()
        # Now docdata has all the info for everyone.
        # Put it into the dict-of-sorted-lists we want for rendering
        bysec = {}
        for sec in SECTIONS:
            bysec[sec] = []
        # Put each item in correct section
        for item in docdata:
            sec = item["section"]
            bysec[sec].append(item)
        # Sort each section
        for sec in bysec:
            bysec[sec] = sorted(bysec[sec], key=lambda k: k['slug'])
        now = time.time()
        mutex.acquire()
        try:
            self.document_data = bysec
            self.document_refresh_time = now
            self.state = self.STATE_READY
        finally:
            mutex.release()

    def get_document_data(self):
        """Return document data.  Use a mutex to make sure we are not
        getting the data while it is being updated."""
        mutex = Lock()
        mutex.acquire()
        try:
            docdata = self.document_data
        finally:
            mutex.release()
        return docdata

    def get_fresh_document_data(self):
        """Return document data, but freshen it first if necessary."""
        if self.check_state() == self.STATE_READY:
            return self.document_data
        self.refresh_document_data()
        return self.get_document_data()

    def check_state(self):
        """Check to see if document data has gone stale, and then return its
        state.
        """
        if self.state != self.STATE_READY:
            # The only automatic transition is READY -> STALE
            return self.state
        now = time.time()
        then = self.document_refresh_time
        if (now - then) > self.max_document_data_age:
            mutex = Lock()
            mutex.acquire()
            try:
                self.state = self.STATE_STALE
            finally:
                mutex.release()
        return self.state

    def render(self, refresh_if_stale=False):
        """Render document data into HTML ul entity with UTF-8 encoding.
        If refresh_if_stale is True, check document freshness, and refresh
        if necessary before rendering.
        """
        docdata = self.get_document_data()
        if not docdata:
            self.info("No document data; refreshing it.")
            self.refresh_document_data()
        if refresh_if_stale and self.check_state() == self.STATE_STALE:
            self.info("Document data is stale; refreshing it.")
            self.refresh_document_data()
        docdata = self.get_document_data()
        if not docdata:
            self.warning("No document data to render.")
            return None
        rdata = self.ul_renderer.render(bysec=docdata).encode('utf-8')
        return rdata

    def render_index(self, refresh_if_stale=False):
        """Render HTML index page with UTF-8 encoding.
        """
        ulist = self.render(refresh_if_stale=refresh_if_stale)
        rdata = self.idx_renderer.render(ul=ulist.decode('utf-8'),
                                         asset_dir="assets").encode('utf-8')
        return rdata

    def _get_docurls(self):
        """Return the list of product URLs that match our sections.
        """
        url = self.keeper_url + "/products"
        resp = requests.get(url)
        raise_from_response(resp)
        plist = resp.json()["products"]
        docurls = []
        for prod in plist:
            for sec in SECTIONS:
                if prod.startswith(url + "/" + sec.lower() + "-"):
                    docurls.append(prod)
                    break
        return docurls

    def _get_keeper_data(self, keeperurl, mutex, docdata):
        try:
            self.debug("Attempting to retrieve %s" % keeperurl)
            resp = retry_request('GET', keeperurl, tries=5, initial_interval=1)
        except BackendError as exc:
            self.error("Failed to retrieve %s: %s", (keeperurl, str(exc)))
            return
        try:
            content = resp.json()
        except JSONDecodeError as exc:
            self.error("Failed to decode %s as JSON" % keeperurl)
            self.error("Received content was %s" % str(resp.content))
            self.error("Error: %s" % str(exc))
            return
        slug = content["slug"]
        section = slug.split('-')[0].upper()
        content["section"] = section
        if "published_url" in content:
            content["dashboard"] = content["published_url"] + "/v"
        else:
            content["dashboard"] = None
        giturl = content["doc_repo"]
        # Completely obvious: throw away the protocol, the double-slash,
        #  the host:port with trailing slash, join the rest back up with
        #  slashes, then throw away the last four characters if they are ".git"
        repoctx = '/'.join(giturl.split('/')[3:])
        if repoctx[-4:] == ".git":
            repoctx = repoctx[:-4]
        mdyurl = "https://raw.githubusercontent.com/" + repoctx + \
                 "/master/metadata.yaml"
        try:
            self.debug("Attempting to retrieve %s -> %s" % (giturl, mdyurl))
            resp = retry_request('GET', mdyurl, tries=5, initial_interval=1)
        except BackendError as exc:
            self.error("Failed to retrieve %s -> %s: %s" % (giturl,
                                                            mdyurl, str(exc)))
            return
        try:
            yml = yaml.safe_load(resp.content)
        except yaml.YAMLError as exc:
            self.error("Failed to decode YAML: %s", str(exc))
            return
        try:
            authors = yml["authors"]
            content["authors"] = authors
        except KeyError:
            self.error("Could not determine authors from metadata.yaml.")
            return
        content["description"] = yml.get("description")
        mutex.acquire()
        try:
            docdata.append(content)
        finally:
            mutex.release()
        return
