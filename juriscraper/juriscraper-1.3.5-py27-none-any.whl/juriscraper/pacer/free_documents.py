import re

import requests
from dateutil.rrule import rrule, DAILY
from lxml.html import tostring

from juriscraper.lib.html_utils import (
    set_response_encoding, clean_html, fix_links_in_lxml_tree,
    get_html_parsed_text
)
from juriscraper.lib.log_tools import make_default_logger
from juriscraper.lib.string_utils import convert_date_string
from juriscraper.pacer.utils import (
    get_pacer_case_id_from_docket_url, make_doc1_url,
    get_pacer_document_number_from_doc1_url, get_court_id_from_url,
    reverse_goDLS_function, is_pdf
)

logger = make_default_logger()


class FreeOpinionReport(object):
    """TODO: document here."""
    EXCLUDED_COURT_IDS = ['casb', 'ganb', 'innb', 'mieb', 'miwb', 'nmib', 'nvb',
                          'ohsb', 'tnwb', 'vib']

    def __init__(self, court_id, cookie):
        self.court_id = court_id
        self.session = requests.session()
        self.session.cookies.set(**cookie)
        super(FreeOpinionReport, self).__init__()

    @property
    def url(self):
        if self.court_id == 'ohnd':
            return 'https://ecf.ohnd.uscourts.gov/cgi-bin/OHND_WrtOpRpt.pl'
        else:
            return ('https://ecf.%s.uscourts.gov/cgi-bin/WrtOpRpt.pl' %
                    self.court_id)

    def query(self, start, end):
        if self.court_id in self.EXCLUDED_COURT_IDS:
            logger.error("Cannot get written opinions report from '%s'. It is "
                         "not provided by the court or is in disuse." %
                         self.court_id)
            return []
        dates = [d.strftime('%m/%d/%Y') for d in rrule(
            DAILY, interval=1, dtstart=start, until=end)]
        responses = []
        for d in dates:
            # Iterate one day at a time. Any more and PACER chokes.
            logger.info("Querying written opinions report for '%s' between %s "
                        "and %s" % (self.court_id, d, d))
            responses.append(self.session.post(
                self.url + '?1-L_1_0-1',
                headers={'User-Agent': 'Juriscraper'},
                verify=False,
                timeout=300,
                files={
                    'filed_from': ('', d),
                    'filed_to': ('', d),
                    'ShowFull': ('', '1'),
                    'Key1': ('', 'cs_sort_case_numb'),
                    'all_case_ids': ('', '0'),
                }
            ))
        return responses

    @staticmethod
    def parse(responses):
        """Using a list of responses, parse out useful information and return it as
        a list of dicts.
        """
        results = []
        court_id = "Court not yet set."
        for response in responses:
            response.raise_for_status()
            court_id = get_court_id_from_url(response.url)
            set_response_encoding(response)
            text = clean_html(response.text)
            tree = get_html_parsed_text(text)
            tree.rewrite_links(fix_links_in_lxml_tree, base_href=response.url)
            opinion_count = int(
                tree.xpath('//b[contains(text(), "Total number of '
                           'opinions reported")]')[0].tail)
            if opinion_count == 0:
                continue
            rows = tree.xpath('(//table)[1]//tr[position() > 1]')
            for row in rows:
                if results:
                    # If we have results already, pass the previous result to
                    # the FreeOpinionRow object.
                    row = FreeOpinionRow(row, results[-1], court_id)
                else:
                    row = FreeOpinionRow(row, {}, court_id)
                results.append(row.as_dict())
        logger.info("Parsed %s results from written opinions report at %s" %
                    (len(results), court_id))
        return results

    def download_pdf(self, pacer_case_id, pacer_document_number):
        """Download a PDF from PACER.

        Note that this doesn't support attachments yet.
        """
        url = make_doc1_url(self.court_id, pacer_document_number, True)
        data = {
            'caseid': pacer_case_id,
            'got_receipt': '1',
        }
        logger.info("GETting PDF at URL: %s with params: %s" % (url, data))
        r = self.session.get(
            url,
            params=data,
            headers={'User-Agent': 'Juriscraper'},
            verify=False,
            timeout=300,
        )
        # The request above sometimes generates an HTML page with an iframe
        # containing the PDF, and other times returns the PDF. Our task is thus
        # to either get the src of the iframe and download the PDF or just
        # return the pdf.
        r.raise_for_status()
        if is_pdf(r):
            return r
        text = clean_html(r.text)
        tree = get_html_parsed_text(text)
        tree.rewrite_links(fix_links_in_lxml_tree,
                           base_href=r.url)
        try:
            iframe_src = tree.xpath('//iframe/@src')[0]
        except IndexError:
            if 'pdf:Producer' in text:
                logger.error("Unable to download PDF. PDF content was placed "
                             "directly in HTML. URL: %s, caseid: %s" %
                             (url, pacer_case_id))
                return None
        r = self.session.get(
            iframe_src,
            headers={'User-Agent': 'Juriscraper'},
            verify=False,
            timeout=300,
        )
        return r


class FreeOpinionRow(object):
    """A row in the Free Opinions report.

    For the most part this is fairly straightforward, however eight courts have
    a different type of report that only has four columns instead of the usual
    five (hib, deb, njb, ndb, ohnb, txsb, txwb, vaeb), and a couple courts
    (areb & arwb) have five columns, but are designed more like the four column
    variants.

    In general, what we do is detect the column count early on and then work
    from there.
    """
    def __init__(self, element, last_good_row, court_id):
        """Initialize the object.

        last_good_row should be a dict representing the values from the previous
        row in the table. This is necessary, because the report skips the case
        name if it's the same for two cases in a row. For example:

        Joe v. Volcano | 12/31/2008 | 128 | The first doc from case | More here
                       | 12/31/2008 | 129 | The 2nd doc from case   | More here

        By having the values from the previous row, we can be sure to be able
        to complete the empty cells.
        """
        super(FreeOpinionRow, self).__init__()
        self.element = element
        self.last_good_row = last_good_row
        self.court_id = court_id
        self.column_count = self.get_column_count()

        # Parsed data
        self.pacer_case_id = self.get_pacer_case_id()
        self.docket_number = self.get_docket_number()
        self.case_name = self.get_case_name()
        self.case_date = self.get_case_date()
        self.pacer_document_number = self.get_pacer_document_number()
        self.document_number = self.get_document_number()
        self.description = self.get_description()
        self.nature_of_suit = self.get_nos()
        self.cause = self.get_cause()

    def __str__(self):
        return '<FreeOpinionRow in %s>\n%s' % (self.court_id,
                                               tostring(self.element))

    def as_dict(self):
        """Similar to the __dict__ field, but excludes several fields."""
        attrs = {}
        for k, v in self.__dict__.items():
            if k not in ['element', 'last_good_row']:
                attrs[k] = v
        return attrs

    def get_column_count(self):
        return len(self.element.xpath('./td'))

    def get_pacer_case_id(self):
        # It's tempting to get this value from the URL in the first cell, but
        # that URL can sometimes differ from the URL used in the goDLS function.
        # When that's the case, the download fails.
        try:
            onclick = self.element.xpath('./td[3]//@onclick')[0]
        except IndexError:
            pass
        else:
            if 'goDLS' in onclick:
                # Sometimes the onclick is something else, like in insb's free
                # opinion report.
                return reverse_goDLS_function(onclick)['caseid']

        # No onclick, onclick isn't a goDLS link, etc. Try second format.
        try:
            # This tends to work in the bankr. courts.
            href = self.element.xpath('./td[1]//@href')[0]
        except IndexError:
            logger.info("No content provided in first cell of row. Using last "
                        "good row for pacer_case_id, docket_number, and "
                        "case_name.")
            return self.last_good_row['pacer_case_id']
        else:
            return get_pacer_case_id_from_docket_url(href)

    def get_docket_number(self):
        try:
            s = self.element.xpath('./td[1]//a/text()')[0]
        except IndexError:
            return self.last_good_row['docket_number']
        else:
            if self.column_count == 4 or self.court_id in ['areb', 'arwb']:
                # In this case s will be something like: 14-90018 Stewart v.
                # Kauanui. split on the first space, left is docket number,
                # right is case name.
                return s.split(' ', 1)[0]
            else:
                return s

    def get_case_name(self):
        cell = self.element.xpath('./td[1]')[0]
        if self.column_count == 4 or self.court_id in ['areb', 'arwb']:
            # See note in docket number
            s = cell.text_content().strip()
            if s:
                return s.split(' ', 1)[1]
            else:
                return self.last_good_row['case_name']
        else:
            try:
                return cell.xpath('.//b')[0].text_content()
            except IndexError:
                return self.last_good_row['case_name']

    def get_case_date(self):
        return convert_date_string(self.element.xpath('./td[2]//text()')[0])

    def get_pacer_document_number(self):
        doc1_url = self.element.xpath('./td[3]//@href')[0]
        return get_pacer_document_number_from_doc1_url(doc1_url)

    def get_document_number(self):
        return self.element.xpath('./td[3]//text()')[0]

    def get_description(self):
        return self.element.xpath('./td[4]')[0].text_content()

    def get_nos(self):
        if self.column_count == 4:
            return None
        try:
            return self.element.xpath('./td[5]/i[contains(./text(), '
                                      '"NOS")]')[0].tail.strip()
        except IndexError:
            return None

    def get_cause(self):
        if self.column_count == 4:
            return None
        try:
            return self.element.xpath('./td[5]/i[contains(./text(), '
                                      '"Cause")]')[0].tail.strip()
        except IndexError:
            return None
