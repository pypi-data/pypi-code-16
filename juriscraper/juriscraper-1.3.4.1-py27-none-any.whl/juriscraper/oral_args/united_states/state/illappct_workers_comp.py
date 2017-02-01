'''
CourtID: illappct
Court Short Name: Ill. App. Ct.
Author: Rebecca Fordon
Reviewer: Mike Lissner
History:
* 2016-06-23: Created by Rebecca Fordon
'''

import ill


class Site(ill.Site):
    def __init__(self, *args, **kwargs):
        super(Site, self).__init__(*args, **kwargs)
        self.court_id = self.__module__
        self.url = 'http://www.illinoiscourts.gov/Media/Appellate/Workers_Comp.asp'
        self.download_url_path = '/td[5]//a[.//img]/@href'
        self.case_name_path = '/td[3]'
        self.docket_number_path = "/td[2]"
