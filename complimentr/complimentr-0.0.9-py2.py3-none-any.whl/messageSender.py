from twilio.rest import TwilioRestClient
from complimentr import settings
import math
import numpy as np


def get_random_compliment_from_list():
    compliments = [
        "I think you are so amazing!",
        "I love you so much",
        "You're the best",
        "You're my favorite",
        "I like being with you",
        "You make me smile",
        "You're absolultely wonderful",
        "Kiss!!!",
        "Your smile is contagious",
        "You're beautiful!",
        "You look great today",
        "You're one smart cookie!",
        "I love you!!!",
        "Is that your picture next to \"charming\" in the dictionary?",
        "Your eyes are breath taking",
        "Being around you makes everything better",
        "Colors seem brighter when you're around",
        "Your hair looks stunning",
        "Being around you is like being on a happy little vacation",
        "You're gorgeous",
        "You're my reason to smile"
    ]
    indexForCompliment = math.trunc(np.random.random()*len(compliments))
    return compliments[indexForCompliment]


def sendCompliment():
    account_id = settings.get_account_sid()
    token = settings.get_account_auth_token()
    TO = settings.get_to_phone_number()
    FROM_ = settings.get_senders_phone_number()
    BODY = get_random_compliment_from_list()

    client = TwilioRestClient(account=account_id, token=token)

    client.messages.create(
        to=TO,
        from_=FROM_,
        body=BODY,
    )
    return
