from soaplib.core.service import DefinitionBase, soap
from soaplib.core.model.primitive import String, Integer

class DemoWebService(DefinitionBase):
    '''
    The demo webservice class.
    This defines methods exposed to clients.
    '''
    def __init__(self, environ):
        '''
        This saves a reference to the request environment on the current instance
        '''
        self.environ = environ
        super(DemoWebService, self).__init__(environ)

    @soap(String, _returns=String)# Soap is typed - we need stuff like this
    def echo(self, text):
        return text
