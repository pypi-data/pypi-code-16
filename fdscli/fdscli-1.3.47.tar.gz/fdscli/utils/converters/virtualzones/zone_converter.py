import json
from fdscli.model.virtualzones.zone import Zone 

class ZoneConverter( object ):
    '''
    Created on Sep 14, 2016
    
    @author: chaithra, Neil
    '''
    @staticmethod
    def build_zone_from_json( j_str ):
        
        zone = Zone()

        if not isinstance( j_str, dict ):
            j_str = json.loads(j_str)
        
        for i in range(len(j_str) + 1):
            uuidKeyName = "am" + str(i) + "_uuid"
            if j_str.has_key(uuidKeyName):
                zone.amList.append(j_str[uuidKeyName])

        zone.zid = j_str.pop( "zone_id", zone.zid )
        zone.name = j_str.pop( "name", zone.name )
        zone.state = j_str.pop( "state", zone.state )
        if zone.state == 4:
            zone.state = "Active"
        else:
            zone.state = "Inactive"
        zone.ztype = j_str.pop( "type", zone.ztype )
        # for now, type has to be VAMG
        zone.ztype = "Virtual-AM"
        zone.zvip = j_str.pop( "vip", zone.zvip )
        zone.iface = j_str.pop( "iface", zone.iface)
        
        return zone 

    @staticmethod
    def to_json( zone ):
        '''
        Convert a zone object to a JSON string
        '''
        
        d = dict()
        
        d["zone_id"] = zone.zid
        d["type"] = zone.ztype
        d["name"] = zone.name
        d["vip"] = zone.zvip
        # state is read-only and thus not needed to be exported
        if zone.iface is not None:
            d["iface"] = zone.iface

        # Starts counting at 1
        i = 1
        for oneAM in zone.amList:
            # Key is "am1_uuid"
            keyStr = "am"
            keyStr += str(i)
            keyStr += "_uuid"
            d[keyStr] = oneAM
            i += 1

        # store how many UUIDs we have
        i -= 1
        d["sizeof_amList"] = i

        result = json.dumps( d )
        
        return result
