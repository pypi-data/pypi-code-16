import pytz

def get_formatted_emails(email_list):
    '''
    generates list of dictionaries for input
    can alter function just in case the dictionary needs to get more complicated
    can replace with [{'email':e} for e in email_list] but might need other arguements added
    '''

    guest_list = []
    for email in email_list:
        temp_dict = {'email': email}
        guest_list.append(temp_dict)
    return guest_list

def get_google_time(date_time, add_offset=True, time_zone='US/Central'):
    '''
    function takes datetime without any offset
    either returns UTC time with offset accounted for or
    returns returns UTC isotime without offset
    '''

    if add_offset is True:
        return pytz.timezone(time_zone).localize(date_time).astimezone(
            pytz.utc).replace(tzinfo=None).isoformat() + 'Z'
    else:
        return date_time.isoformat() + 'Z'

def make_event_body(body, summary, attendees, start_time, end_time,
                    time_zone_str='America/Chicago'):
    '''
    description body needs to be indented like that or else indented in email
    '''

    event_body = {
        'description': body,
        'summary': summary,
        'location': 'Austin Tech kitchen',
        'start':  {'dateTime': start_time, 'timeZone': time_zone_str},
        'end':    {'dateTime': end_time, 'timeZone': time_zone_str},
        'attendees': attendees,
        'guestsCanInviteOthers': True,
        'guestsCanModify': True,
        'guestsCanSeeOtherGuests': True,
        'reminders': {'useDefault': True},
    }
    return event_body
