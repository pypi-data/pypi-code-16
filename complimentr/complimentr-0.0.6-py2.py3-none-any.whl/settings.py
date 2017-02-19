from complimentr.ask_user_for_info import askForSettings

def get_account_sid():
    ACCOUNT_SID = askForSettings("Twilio Account ID: ")
    return ACCOUNT_SID

def get_account_auth_token():
    AUTH_TOKEN = askForSettings("Twilio AUTH_TOKEN: ")
    return AUTH_TOKEN

def get_to_phone_number():
    TO= askForSettings("To Phone Number \"+18001234567\": ")
    return TO

def get_senders_phone_number():
    FROM_= askForSettings("From Phone Number \"+18007654321\": ")
    return FROM_
