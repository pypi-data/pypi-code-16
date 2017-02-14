from amaascore.parties.organisation import Organisation


class GovernmentAgency(Organisation):

    def __init__(self, asset_manager_id, party_id, description='', references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.party_id = party_id
        self.references = references
        super(GovernmentAgency, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                               description=description, references=references, *args, **kwargs)
