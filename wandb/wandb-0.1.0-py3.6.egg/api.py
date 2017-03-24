from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

class Api(object):
    """W&B Api wrapper"""
    def __init__(self):
        self.client = Client(
            retries=3,
            transport=RequestsHTTPTransport(
                use_json=True,
                url='http://localhost:5000/graphql'
            )
        )

    def list_models(self):
        """Lists models in W&B"""
        query = '''
        {
            models(first: 10, entity: "models") {
                edges {
                    node {
                        ndbId
                        description
                    }
                }
                
            }
        }
        '''
        return self.client.execute(query)


    def upload_weights(self, attrs):
        """Creates a model in W&B"""
        return self.client.post()
        