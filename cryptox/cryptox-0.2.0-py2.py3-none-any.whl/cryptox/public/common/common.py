#exchange/field_collected/url
endpoints = {
    'poloniex':{
        '24_hour_volume':'https://poloniex.com/public?command=return24hVolume',
        'order_book':'https://poloniex.com/public?command=returnOrderBook',
        'trade_history':'https://poloniex.com/public?command=returnTradeHistory'
        
    },
    'ccex':{ 
        '24_hour_volume':'https://c-cex.com/t/api_pub.html?a=getmarketsummaries',
        'order_book':'https://c-cex.com/t/api_pub.html?a=getorderbook',
        'trade_history':'https://c-cex.com/t/api_pub.html?a=getmarkethistory'
    }
}