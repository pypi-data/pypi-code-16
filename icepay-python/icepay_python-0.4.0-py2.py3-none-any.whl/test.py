from client import IcepayClient

merchant_id = 30184
secret_code = 'd9BYb76Ptx3JLp54ZsMg83Xwu9F4Qaf8UNr7c5TG'

client = IcepayClient(merchant_id, secret_code)

print(client.getBasicPaymentURL({
    'IC_OrderID': 123,
    'IC_Amount': 100,
    'IC_Currency': 'EUR',
    'IC_Country': 'LT',
    'IC_URLCompleted': 'http://example.com/success',
    'IC_URLError': 'http://example.com/fail'
}))