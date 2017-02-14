from amaascore.parties.company import Company


class Fund(Company):

    def __init__(self, asset_manager_id, party_id, references={}, *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.party_id = party_id
        self.references = references
        super(Fund, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id, references=references,
                                   *args, **kwargs)
