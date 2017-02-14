from amaascore.parties.party import Party


class Organisation(Party):

    def __init__(self, asset_manager_id, party_id, party_class=None, description='', references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.party_id = party_id
        if not hasattr(self, 'party_class'):  # A more specific child class may have already set this
            self.party_class = 'Organisation'
        self.references = references
        super(Organisation, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                           description=description, references=references, *args, **kwargs)
