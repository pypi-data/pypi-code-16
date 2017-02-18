from twilio.rest import TwilioRestClient
from config import settings

def sendCompliment():
    client = TwilioRestClient(settings.ACCOUNT_SID, settings.AUTH_TOKEN)

    client.messages.create(
        to=settings.TO,
        from_=settings.FROM_,
        body="I think you are so amazing!",
        media_url="https://c1.staticflickr.com/3/2899/14341091933_1e92e62d12_b.jpg",
    )
    return
