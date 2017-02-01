from .abstract_service import AbstractService

from fdscli.utils.converters.virtualzones.zone_converter import ZoneConverter
from fdscli.model.fds_error import FdsError

class ZoneService( AbstractService ):
    '''
    Created on Sep 15, 2016

    @author: chaithra, NeilH
    '''

    def __init__(self, session):
        AbstractService.__init__(self, session)

    def create_zone(self, zone):
        '''
        Create a VAMG

        '''
        url = "{}{}".format( self.get_url_preamble(), "/virtualzones" )
        data = ZoneConverter.to_json( zone )
        j_zone =  self.rest_helper.post( self.session, url, data )

        if isinstance(j_zone, FdsError):
            return j_zone

        return 0

    def activate_zones(self, zone_ids):
        '''
        activate a list of zones
        '''

        url = "{}{}{}".format(self.get_url_preamble(), "/virtualzones/activate/", zone_ids)
        response = self.rest_helper.get(self.session, url)

        return response

    def deactivate_zones(self, zone_ids):
        '''
        deactivate a list of zones
        '''

        url = "{}{}{}".format(self.get_url_preamble(), "/virtualzones/deactivate/", zone_ids)
        response = self.rest_helper.get(self.session, url)

        return response

    def delete_zone(self, zone_id):
        '''
        delete a single zone
        '''

        url = "{}{}{}".format(self.get_url_preamble(), "/virtualzones/", zone_id)
        response = self.rest_helper.delete(self.session, url)

        if isinstance(response, FdsError):
            return response

        return

    def list_zones(self):

        '''
        Return the raw json list of zones from the FDS REST call
        '''
        url = "{}{}".format(self.get_url_preamble(), "/virtualzones")
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        zones = []

        for j_zone in response:
            zone = ZoneConverter.build_zone_from_json(j_zone)
            zones.append(zone)

        return zones

    def get_zone(self, zone_id):
        '''
        get a single zone
        '''

        url = "{}{}{}".format(self.get_url_preamble(), "/virtualzones/", zone_id)
        response = self.rest_helper.get(self.session, url)

        if isinstance(response, FdsError):
            return response

        if len(response) > 0:
            zone = ZoneConverter.build_zone_from_json(response[0])
        else:
            print "The requested zone %d could not be found." % (zone_id)
            return

        return zone
