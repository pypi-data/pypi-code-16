"""
This module contains abstractions which are useful for describing and
manipulating what you find on the page when you click `Active Foreign Principals`
on FARA's home page.

This Active Principal page contains a list of Foreign Principals with 
partial or incomplete details of an active principal. Clicking on the link
of a Principal takes you to the details page of the principal where you can
view it's exhibits.

In this component, the collection of details you find on the list page is
refered to as a `Partial Principal` because it contains incomplete/partial
data for the principal (it does not contain it's exhibit information). After
the principal's exhibit infos has been appended to the details gotten from 
the list page, it can then be refered to as a `Full Principal` or `Principal`
for short.

The first list or pagination of principals you see when you navigate to
the `Active Principals` web page, contains some special information hidden
in it. This information is needed to navigate from one page to another
for the user's session. If this set of information is not passed on, the
web app intelligently detects that it is being scraped, then it returns 
a 404 not found error message to confuse people who write scrappers. This
information which can only be gotten from the first list page is refered
to as the `Page Context` in this core module.
"""

import copy

import requests
from scrapy import Selector

from fara_principals.core.principals import ForeignPrincipal, Exhibit
from fara_principals.exceptions import (
    InvalidPrincipalError, PageInstanceInfoNotFoundError, PageError,
    InvalidExhibitError, PaginationEndedError
)

#url to the first/main list page which contains the first set of paginated
#principals
__main_url__ = \
    'https://efile.fara.gov/pls/apex/f?p=171:130:0::NO:RP,130:P130_DATERANGE:N'

#default template for a page's contextual information
__default_page_context__ = {
    "instance_id": None, "flow_id": None, "flow_step_id": None,
    "worksheet_id": None, "report_id": None, "page": 1
}

#default template of form date which will be used to request for the next page
__default_next_page_form_data__ = {
    "p_request": "APXWGT",
    "p_instance": None,
    "p_flow_id": None,
    "p_flow_step_id": None,
    "p_widget_num_return": "15",
    "p_widget_name": "worksheet",
    "p_widget_mod": "ACTION",
    "p_widget_action": "PAGE",
    "p_widget_action_mod": "pgR_min_row=1max_rows=15rows_fetched=15",
    "x01": None,
    "x02":None,
}

#initial safe headers that wont flag users as a scraper
__init_headers__ = {
   "Accept": "*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control":"no-cache",
    "Connection": "keep-alive",
    "Host": "efile.fara.gov",
    "Origin": "https://efile.fara.gov",
    "Pragma": "no-cache",
    "Referer": "https://efile.fara.gov/pls/apex/f?p=171:1:0:::::",
    "User-Agent" : "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"
    }

class PrincipalListPage:
    """
    Page class with useful helpers responsible for navigating a paginated
    page containing Foreign Principal information.

    Args:
        url(str): url of the page being accessed

    Keyword Args:
        content(str): (optional) content of the page whose structure is to be
            parsed for principal entries.

        page_context(dict): (optional) a dict containing contextual info
            about a page. This contextual info are necessary to navigate
            from one page to another else, the server detects it's been 
            scraped which makes it return 404 not found pages thereby
            confusing it's scrappers.

    Notes: the main (first) page contains the contextual infos in hidden
    html inputs so, it's not necessary for users to pass this info for 
    the main page. However, this info is needed for subsequent pages. The 
    context info can be provided to subsequent pages by calling 
    `self.get_page_context()`, and then passing it to the constructor of 
    subsequent pages.
    """

    def __init__(self, url, content=None, page_context={}, *args, **kwargs):
        self._url = url
        self._content = content
        if self._content:
            self._content = self._content.replace('&nbsp;', ' ')

        self._cookies = None
        if self.is_main_page():
            self._build_main_page()
        else:
            self._build_normal_page()

        self._page_context = None
        self._page_context = page_context or self.get_page_context()

    def is_main_page(self):
        """
        Returns:
            bool: True if the url for this page is that of the main 
            active foreign principal web page.
        """
        return self._url == __main_url__

    def get_page_context(self):
        """
        Returns:
            dict: a dict containing details including the server-tracked
            page instance id and other server-tracked details which are 
            necessary to make further requests to the server.

        Raises:
            PageinstanceInfoNotFoundError: when an important page context
            variable is not found in the loaded html page.
        """
        #print(self._content)
        if self._page_context:
            return self._page_context

        context = copy.deepcopy(__default_page_context__)
        context["instance_id"] = self._page_instance_id()
        context["flow_id"] = self._page_flow_id()
        context["flow_step_id"] = self._page_flow_step_id()
        context["worksheet_id"] = self._page_worksheet_id()
        context["report_id"] = self._page_report_id()
        
        return context

    def _page_instance_id(self):
        try:
            instance_id = Selector(text=self._content).\
                xpath('//input[@name="p_instance"]/@value').extract()[0]
            return str(instance_id)
        except Exception:
            raise PageInstanceInfoNotFoundError("page data {} not found".\
                format("instance_id"))

    def _page_flow_id(self):
        try:
            flow_id = Selector(text=self._content).\
                xpath('//input[@name="p_flow_id"]/@value').extract()[0]
            return str(flow_id)
        except Exception:
            raise PageInstanceInfoNotFoundError("page data {} not found".\
                format("flow_id"))

    def _page_flow_step_id(self):
        try:
            flow_step_id = Selector(text=self._content).\
                xpath('//input[@name="p_flow_step_id"]/@value').extract()[0]
            return str(flow_step_id)
        except Exception:
            raise PageInstanceInfoNotFoundError("page data {} not found".\
                format("flow_step_id"))

    def _page_worksheet_id(self):
        try:
            page_selector = Selector(text=self._content)
            return str(page_selector.xpath(
                '//input[@id="apexir_WORKSHEET_ID"]/@value').extract()[0])
        except Exception:
            raise PageInstanceInfoNotFoundError("page data {} not found".\
                format("worksheet_id"))

    def _page_report_id(self):
        try:
            page_selector = Selector(text=self._content)
            return str(page_selector.xpath(
                '//input[@id="apexir_REPORT_ID"]/@value').extract()[0])
        except Exception:
            raise PageInstanceInfoNotFoundError("page data {} not found".\
                format("report_id"))

    def _build_main_page(self):
        """
        Builds the necessary internal structures for the first page since
        the first page has some extra requirements
        """
        init_headers = copy.deepcopy(__init_headers__)
        init_r = requests.get(__main_url__, headers=init_headers)
        self._content = init_r.text.replace('&nbsp;', ' ')
        self._cookies = init_r.history[0].cookies.get_dict()

    def _build_normal_page(self):
        pass

    def next_page_form_data(self):
        """
        Contructs a dict which contains the form data needed to request the
        next page.

        Returns:
            dict: next page form data

        Raises:
            PaginationEndedError: if the current page contains no more
            principals.
        """
        if not self.partial_principals():
            raise PaginationEndedError(
                "the current page {} contain no more data, the next wont"\
                .format(self.get_page_context()["page"]))

        form_data = copy.deepcopy(__default_next_page_form_data__)
        page_context = self.get_page_context()

        page_content_count = 15
        min_rows = ((page_context["page"] - 1) * page_content_count) + 1
        max_rows = min_rows + page_content_count -1
        calculated_action = "pgR_min_row={}max_rows={}rows_fetched={}".format(
            min_rows, max_rows, page_content_count)

        form_data["p_instance"] = page_context["instance_id"]
        form_data["p_flow_id"] = page_context["flow_id"]
        form_data["p_flow_step_id"] = page_context["flow_step_id"]
        form_data["p_widget_action_mod"] = calculated_action
        form_data["x01"] = page_context["worksheet_id"]
        form_data["x02"] = page_context["report_id"]

        return form_data

    def next_page_url(self):
        """
        Constructs a url for the request of the next page to be retrieved

        Returns:
            str: the url of the next page to be which would be opened if
            the next button had been clicked in the browser.

        Raises:
            PaginationEndedError: if the current page contains no more
            principals.
        """
        if not self.partial_principals():
            raise PaginationEndedError(
                "the current page {} contain no more data, the next wont"\
                .format(self.get_page_context()["page"]))
        return "https://efile.fara.gov/pls/apex/wwv_flow.show"

    def main_page_cookie(self):
        """
        Returns:
            dict: a cookie in form of a dict which will be used to make
            requests for the next page.

        Raises:
            PageError: when called on a page which is not the main page
        """
        return self._cookies

    def partial_principals(self):
        """
        Returns:
            list: a list of ForeignPrincipal instances that have been
            extracted from the current page.
        """
        country_dicts = self._country_dicts()
        partial_principal_dicts = self._partial_principal_dicts()
        partial_principals = []

        for country_dict in country_dicts:
            for partial_principal_dict in partial_principal_dicts:

                if self._country_owns_principal(country_dict, 
                partial_principal_dict):

                    partial_principal_dict["country"] = country_dict["name"]
                    #copy to prevent KeyError on the dict on next iteration
                    p_dict = copy.deepcopy(partial_principal_dict)
                    self._discard_unwanted_fields(p_dict)
                    partial_principals.append(
                        ForeignPrincipal(partial_dict=p_dict))

        return partial_principals

    def _country_owns_principal(self, country_dict, principal_dict):
        return country_dict["country_page_index"] == \
            principal_dict["country_page_index"]

    def _discard_unwanted_fields(self, principal_dict):
        del principal_dict["country_page_index"]
        return principal_dict

    def _country_dicts(self):
        """
        returns dict containing country names and thier position index
        as they appear on the page
        """
        country_table_headers = self._all_country_table_headers()
        country_dicts = []
        for country_table_header in country_table_headers:
            _country_id = country_table_header.xpath('@id').extract()
            country_index = int(_country_id[0].rsplit("_", 1)[1])
            country_name = ''.join(country_table_header.xpath(
                './/span[@class="apex_break_headers"]/text()').extract())
            country_dicts.append(dict(name=country_name, 
                country_page_index=country_index))

        return country_dicts

    def _all_country_table_headers(self):
        """
        returns all <th> containing county names
        """
        page_selector = Selector(text=self._content)
        return page_selector.xpath(
            '//th[starts-with(@id, "BREAK_COUNTRY_NAME")]')

    def _partial_principal_dicts(self):
        """
        returns dict containing infos like `principal name`, `reg_date`, 
        etc, this collection of info is named a partial principal because
        it contains only a subset of all the data needed to create a full
        foreign principal because it doesn't contain any exhibition info.
        To make a partial principal a complete principal, it's exhibition 
        info from the details page of a principal must be added it.
        """
        principal_dicts = []
        principal_table_datas = self._all_principal_td()
        for principal_table_data in principal_table_datas:
            country_page_index = int(principal_table_data.xpath('@headers').\
                extract()[0].rsplit('_',1)[1])

            link = ''.join(
                principal_table_data.xpath('.//a/@href').extract())
            link = 'https://efile.fara.gov/pls/apex/' + link

            principal_name = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "FP_NAME")]/text()').\
                    extract())

            principal_reg_date = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "FP_REG_DATE")]/text()').\
                    extract())

            address = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "ADDRESS_1")]/text()').\
                    extract())

            state = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "STATE")]/text()').extract())

            registrant = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "REGISTRANT_NAME")]/text()').\
                    extract())

            reg_number = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "REG_NUMBER")]/text()').\
                    extract())

            reg_date = ''.join(principal_table_data.xpath(
                '..//td[starts-with(@headers, "REG_DATE")]/text()').\
                    extract())

            principal_dicts.append(dict(country_page_index=country_page_index,
                url=link, principal_name=principal_name, 
                principal_reg_date=principal_reg_date, address=address, 
                state=state, registrant=registrant, reg_number=reg_number,
                reg_date=reg_date, exhibit=[]))

        return principal_dicts

    def _all_principal_td(self):
        page_selector = Selector(text=self._content)
        return page_selector.xpath(
            '//td[starts-with(@headers, "LINK BREAK_COUNTRY_NAME")]')

class ExhibitPage:

    def __init__(self, content, *args, **kwargs):
        self._content = content

    def exhibits(self):
        exhibits = []
        exhibit_dicts = self._all_exhibit_dicts()
        for exhibit_dict in exhibit_dicts:
            exhibits.append(Exhibit(exhibit_dict=exhibit_dict))

        return exhibits

    def _all_exhibit_dicts(self):
        exhibit_selectors = self._all_exhibit_rows()
        exhibit_dicts = []
        for selector in exhibit_selectors:
            date_stamped = ''.join(selector.xpath(
                './/td[@headers="DATE_STAMPED"]/text()').extract())
            document_link = ''.join(selector.xpath(
                './/td[@headers="DOCLINK"]/a/@href').extract())
            reg_number = ''.join(selector.xpath(
                './/td[@headers="REGISTRATION_NUMBER"]/text()').extract())
            registrant = ''.join(selector.xpath(
                './/td[@headers="REGISTRANT_NAME"]/text()').extract())
            document_type = ''.join(selector.xpath(
                './/td[@headers="DOCUMENT_TYPE"]/text()').extract())

            exhibit_dicts.append(dict(date_stamped=date_stamped, 
                document_link=document_link, reg_number=reg_number,
                registrant=registrant, document_type=document_type))

        return exhibit_dicts

    def _all_exhibit_rows(self):
        return Selector(text=self._content).xpath(
            '//table[@class="apexir_WORKSHEET_DATA"]/tr[@class="even"] | ' + \
            '//table[@class="apexir_WORKSHEET_DATA"]/tr[@class="odd"]')