from amaascore.parties.organisation import Organisation


class GovernmentAgency(Organisation):

    def __init__(self, asset_manager_id, party_id, description='', party_status='Active',
                 addresses={}, emails={}, links={}, references={},
                 *args, **kwargs):
        super(GovernmentAgency, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                               description=description, party_status=party_status,
                                               addresses=addresses, emails=emails,
                                               links=links, references=references, *args, **kwargs)
