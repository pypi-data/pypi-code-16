
from . import _VDAPIService, _VDDuplicateableResponse

class _DemandTagAPI(_VDAPIService):

    __RESPONSE_OBJECT__ = _VDDuplicateableResponse
    __API__ = "demand_tags"

class _DemandPartnerAPI(_VDAPIService):

    __API__ = "demand_partners"

class _DemandGroupAPI(_VDAPIService):

    __API__ = "demand_groups"






