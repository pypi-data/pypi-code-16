from datetime import date

from juriscraper.OpinionSite import OpinionSite
from juriscraper.AbstractSite import logger, InsanityException
from juriscraper.lib.string_utils import convert_date_string


class Site(OpinionSite):
    required_headers = ['Date', 'Docket', 'Name', 'J.']
    expected_headers = required_headers + ['Revised', 'R-', 'Pt.']
    justices = {
        'A': 'Samuel Alito',
        'AS': 'Antonin Scalia',
        'B': 'Stephen Breyer',
        'D': 'Decree',
        'DS': 'David Souter',
        'EK': 'Elana Kagan',
        'G': 'Ruth Bader Ginsburg',
        'JS': 'John Paul Stephens',
        'K': 'Anthony Kennedy',
        'PC': 'Per Curiam',
        'R': 'John G. Roberts',
        'SS': 'Sonia Sotomayor',
        'T': 'Clarence Thoma',
    }

    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.court_id = self.__module__
        self.yy = date.today().strftime('%y')
        self.back_scrape_iterable = range(6, int(self.yy) + 1)
        self.url_base = 'https://www.supremecourt.gov/opinions'
        self.path_table = "//table[@class='table table-bordered']"
        self.path_row = '%s/tr[position() > 1]' % self.path_table
        self.precedential = 'Published'
        self.court = 'slipopinion'
        self.running_back_scraper = False
        self.headers = False
        self.url = False
        self.headers = []
        self.cases = []

    def _download(self, request_dict={}):
        if self.method != 'LOCAL' and not self.running_back_scraper:
            self.set_url()
        html = super(Site, self)._download(request_dict)
        self.extract_cases_from_html(html)
        return html

    def set_url(self):
        self.url = '%s/%s/%s' % (self.url_base, self.court, self.yy)

    def set_table_headers(self, html):
        # Do nothing if table is missing
        if html.xpath(self.path_table):
            path = '%s//th' % self.path_table
            self.headers = [cell.text_content().strip() for cell in html.xpath(path)]
            # Ensure that expected/required headers are present
            if not set(self.required_headers).issubset(self.headers):
                raise InsanityException('Required table column missing')

    def extract_cases_from_html(self, html):
        self.set_table_headers(html)
        for row in html.xpath(self.path_row):
            case = self.extract_case_data_from_row(row)
            if case:
                # Below will raise key error is new judge key encountered (new SC judge appointed)
                case['judge'] = self.justices[case['J.']] if case['J.'] else ''
                self.cases.append(case)
                if 'Revised' in case and 'Revised_Url' in case:
                    revision = case.copy()
                    revision['Date'] = case['Revised']
                    revision['Name_Url'] = case['Revised_Url']
                    self.cases.append(revision)

    def extract_case_data_from_row(self, row):
        case = {}
        cell_index = 0
        # Process each cell in row
        for cell in row.xpath('./td'):
            text = cell.text_content().strip()
            # Skip blank rows with blank first cell
            if cell_index == 0 and not text:
                break
            label = self.headers[cell_index]
            # We only care about certain columns
            if label not in ['R-', 'Pt.']:
                case[label] = text
                href = cell.xpath('./a/@href')
                if href:
                    case[label + '_Url'] = href[0]
            cell_index += 1
        return case

    def _get_case_names(self):
        return [case['Name'] for case in self.cases]

    def _get_download_urls(self):
        return [case['Name_Url'] for case in self.cases]

    def _get_case_dates(self):
        return [convert_date_string(case['Date']) for case in self.cases]

    def _get_docket_numbers(self):
        return [case['Docket'] for case in self.cases]

    def _get_judges(self):
        return [case['judge'] for case in self.cases]

    def _get_precedential_statuses(self):
        return [self.precedential] * len(self.cases)

    def _download_backwards(self, d):
        yy = str(d if d >= 10 else '0{}'.format(d))
        logger.info("Running backscraper for year: 20%s" % yy)
        self.running_back_scraper = True
        self.set_url()
        self.url = self.url.replace(self.yy, yy)
        self.html = self._download()
