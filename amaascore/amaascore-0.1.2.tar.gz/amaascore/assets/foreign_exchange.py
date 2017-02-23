from amaascore.assets.asset import Asset


class ForeignExchangeBase(Asset):
    """ This class should never be instantiated """

    def __init__(self, asset_id, asset_status='Active', description='', country_id=None,
                 client_id=None, references={}, *args, **kwargs):
        if not hasattr(self, 'asset_class'):  # A more specific child class may have already set this
            self.asset_class = 'ForeignExchange'
        super(ForeignExchangeBase, self).__init__(asset_manager_id=0, asset_id=asset_id, fungible=True,
                                                  asset_status=asset_status, description=description,
                                                  country_id=country_id, references=references, client_id=client_id,
                                                  *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:2]

    def counter_currency(self):
        return self.asset_id[3:5]


class ForeignExchange(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """
    def __init__(self, asset_id, asset_status='Active', description='', client_id=None, *args, **kwargs):
        self.deliverable = True
        super(ForeignExchange, self).__init__(asset_id=asset_id, asset_status=asset_status, description=description,
                                              client_id=client_id, *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:3]

    def counter_currency(self):
        return self.asset_id[3:6]


class NonDeliverableForward(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """

    def __init__(self, asset_id, asset_status='Active', description='', client_id=None, *args, **kwargs):
        self.deliverable = False
        super(NonDeliverableForward, self).__init__(asset_id=asset_id, asset_status=asset_status,
                                                    description=description, client_id=client_id, *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:3]

    def counter_currency(self):
        return self.asset_id[3:6]
