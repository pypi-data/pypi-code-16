import os

from complimentr.ask_user_for_info import askForSettings

def get_account_sid():
    return fetch_config('TWILIO_ACCOUNT_SID', "Twilio Account ID: ")

def get_account_auth_token():
    return fetch_config('TWILIO_AUTH_TOKEN', "Twilio AUTH_TOKEN: ")

def get_senders_phone_number():
    return fetch_config('FROM_PHONE', "Twilio's Phone Number: ", formatAsPhoneNumber)

def get_to_phone_number():
    return fetch_config('TO_PHONE', "To Phone Number: ", formatAsPhoneNumber)

def fetch_config(env_var, prompt, formatter=None):
    try:
        return os.environ[env_var]
    except KeyError:
        value = askForSettings(prompt)
        return formatter(value) if formatter else value

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
