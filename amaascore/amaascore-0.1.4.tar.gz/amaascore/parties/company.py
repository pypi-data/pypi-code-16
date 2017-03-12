from amaascore.parties.organisation import Organisation


class Company(Organisation):

    def __init__(self, asset_manager_id, party_id, base_currency=None, description='', party_status='Active',
                 addresses={}, emails={}, links={}, references={},
                 *args, **kwargs):
        if not hasattr(self, 'party_class'):  # A more specific child class may have already set this
            self.party_class = 'Company'
        super(Organisation, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id,
                                           base_currency=base_currency, description=description,
                                           party_status=party_status,
                                           addresses=addresses, emails=emails, links=links, references=references,
                                           *args, **kwargs)
