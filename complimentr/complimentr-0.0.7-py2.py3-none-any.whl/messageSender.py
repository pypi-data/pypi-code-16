from twilio.rest import TwilioRestClient
from complimentr import settings

def sendCompliment():
    account_id = settings.get_account_sid()
    token = settings.get_account_auth_token()
    TO = settings.get_to_phone_number()
    FROM_ = settings.get_senders_phone_number()

    client = TwilioRestClient(account=account_id, token=token)

    client.messages.create(
        to=TO,
        from_=FROM_,
        body="I think you are so amazing!",
        media_url="https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg",
    )
    return
