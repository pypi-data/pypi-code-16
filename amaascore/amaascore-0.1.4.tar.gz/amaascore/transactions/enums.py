TRANSACTION_TYPES = {'Allocation', 'Block', 'Cashflow', 'Coupon', 'Dividend', 'Exercise', 'Expiry', 'Payment',
                     'Journal', 'Maturity', 'Net', 'Novation', 'Trade'}
TRANSACTION_LIFECYCLE_ACTIONS = {'Acquire', 'Remove'}
TRANSACTION_ACTIONS = {'Buy', 'Sell', 'Short Sell', 'Deliver', 'Receive'} | TRANSACTION_LIFECYCLE_ACTIONS
TRANSACTION_CANCEL_STATUSES = {'Cancelled', 'Netted', 'Novated'}
TRANSACTION_STATUSES = {'New', 'Amended', 'Superseded'} | TRANSACTION_CANCEL_STATUSES
