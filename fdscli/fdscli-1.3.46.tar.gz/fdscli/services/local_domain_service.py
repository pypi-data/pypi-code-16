from .abstract_service import AbstractService

from fdscli.model.fds_error import FdsError
from fdscli.model.platform.domain import Domain
from fdscli.utils.converters.platform.domain_converter import DomainConverter

class LocalDomainService( AbstractService ):
    '''
    Created on Apr 28, 2015
    
    @author: nate
    '''

    def __init__(self, session):
        AbstractService.__init__(self, session)

    def find_domain_by_id(self, domain_id):
        '''
        Deprecated. In use before GET 'local_domains/<domain_id>' was white-listed.
        '''
        domains = self.get_local_domains()
        
        for domain in domains:
            if int(domain.id) == int(domain_id):
                return domain
            
        return None

    def get_local_domain(self, domain_id):
        '''Get local domain given Id

        Parameters
        ----------
        domain_id (int) : local domain Id

        Returns
        -------
        model.platform.Domain
        '''
        url = "{}{}{}".format( self.get_url_preamble(), "/local_domains/", domain.id )
        j_domain = self.rest_helper.get( self.session, url )

        if isinstance(j_domain, FdsError):
            return j_domain;

        domain = DomainConverter.build_domain_from_json( j_domain )
        return domain

    def get_local_domains(self):
        '''
        Retrieve a list of local domains
        '''
        
        url = "{}{}".format(self.get_url_preamble(), "/local_domains")
        j_domains = self.rest_helper.get( self.session, url )
        
        if isinstance(j_domains, FdsError):
            return j_domains
        
        domains = []
        
        for j_domain in j_domains:
            domain = DomainConverter.build_domain_from_json( j_domain )
            # FS-6973: The GET 'local_domains' endpoint defaults domain state to UP.
            # The white-listed endpoint GET 'local_domains/<domain id>' supplies the
            # domain state maintained by native OM. TODO: Enhance GET 'local_domains'
            # to supply accurate domain state.
            url = "{}{}{}".format( self.get_url_preamble(), "/local_domains/", domain.id )
            j_d = self.rest_helper.get( self.session, url )

            if isinstance(j_d, FdsError):
                domain.state = Domain.STATE_UNKNOWN
                domains.append( domain )
            else:
                domain = DomainConverter.build_domain_from_json( j_d )
                domains.append( domain )
            
        return domains
    
    def shutdown(self, domain):
        '''
        Shutdown the specified domain
        '''
        
        url = "{}{}{}".format( self.get_url_preamble(), "/local_domains/", domain.id )
        # Using given domain as a data transfer object, where desired domain state is DOWN
        domain.state = Domain.STATE_DOWN
        data = DomainConverter.to_json(domain)
        response = self.rest_helper.put( self.session, url, data )
        
        if isinstance(response, FdsError):
            return response
        
        return response        
    
    def start(self, domain):
        '''
        start up the specified domain
        '''
        
        url = "{}{}{}".format( self.get_url_preamble(), "/local_domains/", domain.id )
        # Using given domain as a data transfer object, where desired domain state is UP
        domain.state = Domain.STATE_UP
        data = DomainConverter.to_json(domain)
        response = self.rest_helper.put( self.session, url, data )
        
        if isinstance(response, FdsError):
            return response
        
        return response        
        
    def check_tokens(self, domain):
        '''
        checks the tokens within the specified domain
        '''
        
        url = "{}{}{}{}".format( self.get_url_preamble(), "/local_domains/", "checkTokens/", domain.id )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response
        
        return response        

    def fix_tokens(self, domain):
        '''
        fixes the tokens within the specified domain
        '''
        
        url = "{}{}{}{}".format( self.get_url_preamble(), "/local_domains/", "fixTokens/", domain.id )
        response = self.rest_helper.get( self.session, url )
        
        if isinstance(response, FdsError):
            return response
        
        return response        
 
