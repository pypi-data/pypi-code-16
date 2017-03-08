from facebookads.adobjects.adreportrun import AdReportRun
import requests


class ExportAdReport(AdReportRun):
    def __init__(self, fbid=None, parent_id=None, api=None):
        self.url = 'https://www.facebook.com/ads/ads_insights/export_report/'
        self._isExportAdReport = True
        super(ExportAdReport, self).__init__(fbid, parent_id, api)


    def download_report(self, fields, export_format, filename):
        '''
        Call this method after async job has been completed.
        Use self.remote_read() to read completion percentage
        '''
        params = {
            'report_run_id': self.get_id_assured(),
            'format': export_format,
            'export_columns[]': fields,
            'access_token': self.get_access_token()
        }
        headers = {
            'Accept-Language': 'en-US'
        }
        resp = requests.get(self.url, params=params, headers=headers)
        return
        with requests.Session() as session:
            response = session.get(self.url, params=params)
            with open(filename, 'wb') as csv_file:
                csv_file.write(response.content)


    def get_access_token(self):
        api = self.get_api_assured()
        access_token = api._session.access_token
        return access_token