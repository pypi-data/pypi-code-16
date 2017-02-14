from amaascore.parties.organisation import Organisation


class Company(Organisation):

    def __init__(self, asset_manager_id, party_id, description='', references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.party_id = party_id
        if not hasattr(self, 'party_class'):  # A more specific child class may have already set this
            self.party_class = 'Company'
        self.references = references
        super(Organisation, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                           description=description, references=references, *args, **kwargs)
