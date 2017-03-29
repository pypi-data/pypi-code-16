import pandas as pd
from dateutil import parser

def get_entity_busy_status(service, start, end, entity_list):
    '''
    check if something is busy, if busy then true if not false
    requires gcal service, start and end time, and list of people you want to get
    the busy status of

    returns: times where the entity(person) is busy in their respective calendar
    '''

    item_list = [{'id':e} for e in entity_list]

    body = {
        "timeMin": start + 'Z',
        "timeMax": end + 'Z',
        "timeZone": 'US/Central',
        #           "items": [{"id": entity}]
        "items": item_list
        }

    return service.freebusy().query(body=body).execute()

def is_dict_in_timerange(start_dt, end_dt, gcal_dict):
    '''
    inputs: start_dt and end_dt (datetime) as well as gcal_dict (google calendar dict)
        from get_entity_busy_status
    outputs: 0 or 1 whether or not start_dt and end_dt intersect any busy time
        in the google calendar dict
    '''
    busy_list = []

    for key, cal_dict in gcal_dict['calendars'].iteritems():
        busy_temp = 0
        busy_dict = cal_dict['busy']
        if not busy_dict:
            if 'errors' in cal_dict:
                busy_list.append([key, 1])
                continue
            else:
                busy_list.append([key, 0])
                continue
        else:
#             iterate through the busy_dict and check if busy times intersect
            for busy in busy_dict:
#                 remove the US/Central offset tzinfo
                temp_start_dt = parser.parse(busy['start']).replace(tzinfo=None)
                temp_end_dt = parser.parse(busy['end']).replace(tzinfo=None)
                if (start_dt <= temp_start_dt < end_dt) or (start_dt < temp_end_dt <= end_dt) \
                    or (temp_start_dt <= start_dt and temp_end_dt >= end_dt):
                    busy_temp = 1

        busy_list.append([key, busy_temp])

    df_busy = pd.DataFrame(busy_list, columns=['subject', 'status'])
    df_busy['start'] = start_dt
    df_busy['end'] = end_dt

    return df_busy

def get_events(service, calendar, start, end, num_events, time_zone_str='America/Chicago'):
    '''
    get all available events in the time frame

    inputs:
    calendar - str of google cal
    start / end - str need to be in google cal time format
    num_events - the max number of events desired to be returned
    time_zone_str - time zone of cal

    return df of event ids
    '''

    events_result = service.events().list(calendarId=calendar, timeMin=start, timeMax=end,
                                          timeZone=time_zone_str, maxResults=num_events,
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    event_list = []
    if not events:
        print 'No upcoming events found.'
    else:
        for event in events:
    # get event ids and other info about meeting
            event_id = event['id']
            if 'summary' in event:
                event_sum = event['summary']
            else:
                event_sum = 'could not get summary'
            start_time = event['start'].get('dateTime')
            end_time = event['end'].get('dateTime')
            if 'attendees' in event:
                event_attendees = event['attendees']
            else:
                event_attendees = 'could not get attendees'
            if 'location' in event:
                location = event['location']
            else:
                location = 'no room currently booked'

            event_stats = [event_id, event_sum, start_time, end_time, location, event_attendees]
            event_list.append(event_stats)
    # shove into dataframe if events_list not empty
    try:
        df_events = pd.DataFrame(event_list, columns=['event_id', 'summary', 'start_time',\
                                                      'end_time', 'location', 'event_attendees'])
    except KeyError:
        df_events = pd.DataFrame()

    return df_events

def add_sub_attendees_to_cal(service, calendar, event_list, to_change, add_to_cal=True):
    '''
    function takes list of events and adds everyone to the event ids in df

    calendar - str google calendar
    event_list - list of event ids to add or subtract
    to_change - email addresses that need to be changed
    add_to_cal - boolean add or subtract (default=True)

    returns list of emails that failed to be added to event
    '''

    failed_to_drop_list = []
    for i in range(0, len(event_list)):
        event = service.events().get(calendarId=calendar, eventId=event_list[i]).execute()

        # if there are existing attendees keep them, if not add to dict
        if add_to_cal is True:
            try:
                event['attendees'] += to_change
            except KeyError:
                event['attendees'] = to_change
        else:
            for email_dict in to_change:
                try:
                    # gets the position in the list
                    email_pos = next(index for (index, d) in enumerate(event['attendees']) \
                                     if d['email'] == email_dict['email'])
                    # delete from attendees
                    event['attendees'].pop(email_pos)
                except:
                    failed_to_drop_list.append(email_dict['email'])

        updated_event = service.events().update(calendarId=calendar, sendNotifications=True,
                                                eventId=event['id'], body=event).execute()

    return failed_to_drop_list
