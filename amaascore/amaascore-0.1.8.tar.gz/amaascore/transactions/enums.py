from __future__ import absolute_import, division, print_function, unicode_literals

TRANSACTION_TYPES = {'Allocation', 'Block', 'Cashflow', 'Coupon', 'Dividend', 'Exercise', 'Expiry', 'Payment',
                     'Journal', 'Maturity', 'Net', 'Novation', 'Trade'}
TRANSACTION_INVESTOR_ACTIONS = {'Subscription', 'Redemption'}
TRANSACTION_LIFECYCLE_ACTIONS = {'Acquire', 'Remove'}
TRANSACTION_ACTIONS = {'Buy', 'Sell', 'Short Sell', 'Deliver', 'Receive'} | TRANSACTION_LIFECYCLE_ACTIONS | \
                      TRANSACTION_INVESTOR_ACTIONS
TRANSACTION_CANCEL_STATUSES = {'Cancelled', 'Netted', 'Novated'}
TRANSACTION_STATUSES = {'New', 'Amended', 'Superseded'} | TRANSACTION_CANCEL_STATUSES
