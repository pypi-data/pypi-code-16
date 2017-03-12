from amaascore.parties.company import Company


class Broker(Company):

    def __init__(self, asset_manager_id, party_id, base_currency=None, description='', party_status='Active',
                 addresses={}, emails={}, links={}, references={},
                 *args, **kwargs):
        super(Broker, self).__init__(asset_manager_id=asset_manager_id, party_id=party_id, base_currency=base_currency,
                                     description=description, party_status=party_status,
                                     addresses=addresses, emails=emails, links=links,
                                     references=references, *args, **kwargs)

# TODO - Add markets covered, products covered
