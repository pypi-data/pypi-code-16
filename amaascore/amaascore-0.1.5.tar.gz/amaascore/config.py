# POTENTIALLY SUPPORT MULTIPLE ENVIRONMENTS

LOCAL = False

if LOCAL:
    ENDPOINTS = {
        'asset_managers': 'http://localhost:8000',
        'assets': 'http://localhost:8000',
        'books': 'http://localhost:8000',
        'corporate_actions': 'http://localhost:8000',
        'market_data': 'http://localhost:8000',
        'monitor': 'http://localhost:8000',
        'parties': 'http://localhost:8000',
        'transactions': 'http://localhost:8000'
    }
else:
    ENDPOINTS = {
        'asset_managers': 'https://c1hes1s60m.execute-api.ap-southeast-1.amazonaws.com/dev',
        'assets': 'https://zc6udsq1nb.execute-api.ap-southeast-1.amazonaws.com/dev',
        'books': 'https://smc367plfg.execute-api.ap-southeast-1.amazonaws.com/dev',
        'corporate_actions': 'https://basklngdyh.execute-api.ap-southeast-1.amazonaws.com/dev',
        'market_data': 'https://f0rpi7vksi.execute-api.ap-southeast-1.amazonaws.com/dev',
        'monitor': 'https://wt50nd7j7l.execute-api.ap-southeast-1.amazonaws.com/dev',
        'parties': 'https://hpihgzmxoc.execute-api.ap-southeast-1.amazonaws.com/dev',
        'transactions': 'https://1w0gb581sl.execute-api.ap-southeast-1.amazonaws.com/dev'
    }
