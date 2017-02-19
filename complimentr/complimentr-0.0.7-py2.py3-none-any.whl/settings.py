from complimentr.ask_user_for_info import askForSettings

def get_account_sid():
    ACCOUNT_SID = askForSettings("Twilio Account ID: ")
    return ACCOUNT_SID

def get_account_auth_token():
    AUTH_TOKEN = askForSettings("Twilio AUTH_TOKEN: ")
    return AUTH_TOKEN

def get_to_phone_number():
    TO = askForSettings("To Phone Number: ")
    TO = formatAsPhoneNumber(TO)
    return TO

def get_senders_phone_number():
    FROM_ = askForSettings("From Phone Number: ")
    FROM_ = formatAsPhoneNumber(FROM_)
    return FROM_

def formatAsPhoneNumber(userInput):
    phoneNumber = str(userInput)
    if(len(phoneNumber) < 7):
        print("Invalid phone number, please run complimentr again")
        return
    elif(len(phoneNumber) == 7):
        area_code = askForSettings("Area Code:")
        phoneNumber = area_code + phoneNumber
    elif(len(phoneNumber) == 10):
        phoneNumber = "+1" + phoneNumber
    elif(len(phoneNumber) == 11):
        phoneNumber = "+" + phoneNumber

    return phoneNumber
