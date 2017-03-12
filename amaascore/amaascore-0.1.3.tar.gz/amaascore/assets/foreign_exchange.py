from amaascore.assets.asset import Asset


class ForeignExchangeBase(Asset):
    """ This class should never be instantiated """

    def __init__(self, asset_id, asset_status, description, *args, **kwargs):
        self.asset_class = 'ForeignExchange'
        super(ForeignExchangeBase, self).__init__(asset_manager_id=0, asset_id=asset_id, fungible=True,
                                                  asset_status=asset_status, description=description,
                                                  *args, **kwargs)

    def base_currency(self):
        return self.asset_id[0:3]

    def counter_currency(self):
        return self.asset_id[3:6]


class ForeignExchange(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """
    def __init__(self, asset_id, asset_status='Active', description='', *args, **kwargs):
        super(ForeignExchange, self).__init__(asset_id=asset_id, asset_status=asset_status, description=description,
                                              *args, **kwargs)


class NonDeliverableForward(ForeignExchangeBase):
    """
    Currently modelling spot and forward as the same, just two different dates on the transaction.  We might need to
    change that.
    """

    def __init__(self, asset_id, asset_status='Active', description='', *args, **kwargs):
        super(NonDeliverableForward, self).__init__(asset_id=asset_id, asset_status=asset_status,
                                                    description=description, *args, **kwargs)

