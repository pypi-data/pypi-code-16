from .AnalysisPost_22Endpoint import AnalysisPost_22Endpoint


class AnalysisEndpoint:
    def __init__(self, api_client):
        self._api_client = api_client

    @property
    def AnalysisPost_22(self):
        """
        :return: AnalysisPost_22Endpoint
        """
        return AnalysisPost_22Endpoint(self._api_client)
        